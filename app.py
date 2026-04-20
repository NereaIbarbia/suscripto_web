from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# --- CONFIGURACIÓN DE BASE DE DATOS Y SESIONES ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.mwaizxcunhxxsryifdnb:Pedorreta123@aws-1-eu-west-1.pooler.supabase.com:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_super_secreta_para_sesiones'
db = SQLAlchemy(app)

# --- CONFIGURACIÓN FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
# 👇 ESTO SOLUCIONA TU ERROR 500: Apuntamos a una ruta estática
login_manager.login_view = 'login_view' 

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# --- DICCIONARIO DE TRADUCCIONES ---
TRADUCCIONES = {
    'es': {
        'agregar': 'Añadir Suscripción', 'precio': 'Precio', 'borrar': 'BORRAR',
        'ajustes': 'AJUSTES', 'inicio': 'Inicio', 'calendario': 'Calendario',
        'ahorros': 'Ahorros', 'idioma': 'Idioma', 'moneda': 'Moneda'
    },
    'en': {
        'agregar': 'Add Subscription', 'precio': 'Price', 'borrar': 'DELETE',
        'ajustes': 'SETTINGS', 'inicio': 'Home', 'calendario': 'Calendar',
        'ahorros': 'Savings', 'idioma': 'Language', 'moneda': 'Currency'
    }
}

# --- MODELO DE DATOS ---
class Suscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=True) # ID del usuario
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_cobro = db.Column(db.String(20), nullable=False) 
    ciclo = db.Column(db.String(20), nullable=False, default="Mensual") 
    autorenovacion = db.Column(db.Boolean, default=True)

# Crear tablas y columnas (Asegurando que todo exista en Supabase)
with app.app_context():
    db.create_all()
    for query in [
        "ALTER TABLE suscripcion ADD COLUMN IF NOT EXISTS ciclo VARCHAR(20) DEFAULT 'Mensual';",
        "ALTER TABLE suscripcion ADD COLUMN IF NOT EXISTS autorenovacion BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE suscripcion ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);"
    ]:
        try:
            db.session.execute(text(query))
            db.session.commit()
        except Exception:
            db.session.rollback()

# --- UTILIDADES ---
TASA_EUR_A_USD = 1.16

def obtener_color(nombre):
    n = nombre.lower()
    if 'netflix' in n: return '#e50914'
    if 'prime' in n or 'amazon' in n: return '#00a8e1'
    if 'spotify' in n: return '#1db954'
    if 'hbo' in n or 'max' in n: return '#5a2e98'
    if 'disney' in n: return '#113ccf'
    if 'youtube' in n: return '#ff0000'
    if 'apple' in n: return '#000000'
    if 'playstation' in n or 'psn' in n: return '#003791'
    if 'xbox' in n: return '#107c10'
    if 'gimnasio' in n or 'gym' in n: return '#e67e22'
    return '#34495e'

@app.context_processor
def inject_configuracion():
    moneda_actual = session.get('moneda', '€')
    idioma_actual = session.get('idioma', 'es')
    textos = TRADUCCIONES.get(idioma_actual, TRADUCCIONES['es'])
    return dict(moneda=moneda_actual, textos=textos)

@app.template_filter('convertir_precio')
def convertir_precio(precio_base):
    moneda_actual = session.get('moneda', '€')
    precio_final = precio_base * TASA_EUR_A_USD if moneda_actual == '$' else precio_base
    return f"{precio_final:.2f}"

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login')
def login_view():
    # Página genérica si intentan entrar sin estar logueados
    return """
    <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>¡Bienvenido a la Demo de Suscripciones!</h2>
        <p>Para entrar en tu cuenta, añade <b>/login-demo/tu_nombre</b> al final de la URL.</p>
        <p><i>Ejemplo: localhost:8080/login-demo/nerea</i></p>
    </div>
    """

@app.route('/login-demo/<username>')
def login_demo(username):
    user = User(id=username)
    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_view'))

# --- RUTAS PRINCIPALES ---

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        nombre = request.form.get('nombre_final') 
        precio = request.form.get('precio')
        fecha = request.form.get('fecha_cobro')
        ciclo = request.form.get('ciclo')
        es_auto = request.form.get('autorenovacion') == 'on'
        
        nueva_sub = Suscripcion(
            user_id=current_user.id, 
            nombre=nombre, 
            precio=float(precio), 
            fecha_cobro=fecha, 
            ciclo=ciclo, 
            autorenovacion=es_auto
        )
        db.session.add(nueva_sub)
        db.session.commit()
        return redirect(url_for('index'))
    
    suscripciones = Suscripcion.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', suscripciones=suscripciones, get_color=obtener_color)

@app.route('/borrar/<int:id>')
@login_required
def borrar(id):
    sub = Suscripcion.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/calendario')
@login_required
def calendario():
    # Ahora el calendario también es privado
    suscripciones = Suscripcion.query.filter_by(user_id=current_user.id).all()
    return render_template('calendario.html', suscripciones=suscripciones, get_color=obtener_color)

@app.route('/ahorro')
@login_required
def ahorro():
    # Ahora los ahorros también son privados
    suscripciones = Suscripcion.query.filter_by(user_id=current_user.id).all()
    total = sum(sub.precio for sub in suscripciones)
    return render_template('ahorro.html', suscripciones=suscripciones, total_gastado=round(total, 2))

@app.route('/ajustes', methods=['GET', 'POST'])
def ajustes():
    lang = request.args.get('lang')
    if lang in TRADUCCIONES:
        session['idioma'] = lang

    if request.method == 'POST':
        nueva_moneda = request.form.get('moneda')
        if nueva_moneda:
            session['moneda'] = nueva_moneda
        return redirect(url_for('ajustes'))
    
    return render_template('ajustes.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)