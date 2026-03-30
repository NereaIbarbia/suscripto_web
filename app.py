from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text # AÑADIMOS ESTO PARA ACTUALIZAR LA BASE DE DATOS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.mwaizxcunhxxsryifdnb:Pedorreta123@aws-1-eu-west-1.pooler.supabase.com:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_super_secreta_para_sesiones'
db = SQLAlchemy(app)

TASA_EUR_A_USD = 1.16

# 1. ACTUALIZAMOS EL MODELO DE DATOS
class Suscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_cobro = db.Column(db.String(20), nullable=False) 
    # NUEVA COLUMNA: Mensual o Anual
    ciclo = db.Column(db.String(20), nullable=False, default="Mensual") 

with app.app_context():
    db.create_all()
    # TRUCO: Intentamos añadir la columna nueva a la base de datos que ya existe
    try:
        db.session.execute(text("ALTER TABLE suscripcion ADD COLUMN ciclo VARCHAR(20) DEFAULT 'Mensual';"))
        db.session.commit()
    except Exception as e:
        db.session.rollback() # Si da error es que la columna ya existe, no pasa nada

# --- MAGIA DE COLORES --- (Esto lo dejas igual que lo tenías)
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
def inject_moneda():
    return dict(moneda=session.get('moneda', '€'))

@app.template_filter('convertir_precio')
def convertir_precio(precio_base):
    moneda_actual = session.get('moneda', '€')
    if moneda_actual == '$':
        precio_final = precio_base * TASA_EUR_A_USD
    else:
        precio_final = precio_base
    return f"{precio_final:.2f}"

# 2. ACTUALIZAMOS LA RUTA PRINCIPAL PARA GUARDAR EL CICLO
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recogemos los datos del nuevo formulario Modal
        nombre = request.form.get('nombre_final') 
        precio = request.form.get('precio')
        fecha = request.form.get('fecha_cobro')
        ciclo = request.form.get('ciclo') # Recogemos si es mensual o anual
        
        nueva_sub = Suscripcion(nombre=nombre, precio=float(precio), fecha_cobro=fecha, ciclo=ciclo)
        db.session.add(nueva_sub)
        db.session.commit()
        return redirect(url_for('index'))
    
    suscripciones = Suscripcion.query.all()
    return render_template('index.html', suscripciones=suscripciones, get_color=obtener_color)

@app.route('/borrar/<int:id>')
def borrar(id):
    sub = Suscripcion.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/calendario')
def calendario():
    suscripciones = Suscripcion.query.all()
    return render_template('calendario.html', suscripciones=suscripciones, get_color=obtener_color)

@app.route('/ahorro')
def ahorro():
    suscripciones = Suscripcion.query.all()
    total = sum(sub.precio for sub in suscripciones)
    return render_template('ahorro.html', suscripciones=suscripciones, total_gastado=round(total, 2))

@app.route('/ajustes', methods=['GET', 'POST'])
def ajustes():
    if request.method == 'POST':
        # Recogemos la moneda seleccionada en el formulario
        nueva_moneda = request.form.get('moneda')
        if nueva_moneda:
            session['moneda'] = nueva_moneda # La guardamos en la sesión
        
        return redirect(url_for('ajustes')) # Recargamos la página
    
    return render_template('ajustes.html')

if __name__ == '__main__':
    app.run(debug=True)