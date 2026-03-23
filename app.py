from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suscripciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_super_secreta_para_sesiones'
db = SQLAlchemy(app)

TASA_EUR_A_USD = 1.16

class Suscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    # AHORA LA FECHA ES UN TEXTO (String) PARA GUARDAR "YYYY-MM-DD"
    fecha_cobro = db.Column(db.String(20), nullable=False) 

with app.app_context():
    db.create_all()

# --- MAGIA DE COLORES ---
# Esta función detecta la palabra y devuelve su color oficial
def obtener_color(nombre):
    n = nombre.lower()
    if 'netflix' in n: return '#e50914' # Rojo Netflix
    if 'prime' in n or 'amazon' in n: return '#00a8e1' # Azul Prime
    if 'spotify' in n: return '#1db954' # Verde Spotify
    if 'hbo' in n or 'max' in n: return '#5a2e98' # Morado HBO
    if 'disney' in n: return '#113ccf' # Azul oscuro Disney
    if 'youtube' in n: return '#ff0000' # Rojo YouTube
    if 'apple' in n: return '#000000' # Negro Apple
    if 'playstation' in n or 'psn' in n: return '#003791' # Azul PS
    if 'xbox' in n: return '#107c10' # Verde Xbox
    if 'gimnasio' in n or 'gym' in n: return '#e67e22' # Naranja
    return '#34495e' # Color por defecto (Gris oscuro elegante)

@app.context_processor
def inject_moneda():
    # Si el usuario no ha elegido nada, por defecto será el Euro (€)
    return dict(moneda=session.get('moneda', '€'))

@app.template_filter('convertir_precio')
def convertir_precio(precio_base):
    moneda_actual = session.get('moneda', '€')
    
    if moneda_actual == '$':
        # Si el usuario eligió Dólares, aplicamos la conversión real
        precio_final = precio_base * TASA_EUR_A_USD
    else:
        # Si es Euro, se queda exactamente igual
        precio_final = precio_base
        
    # Devolvemos el número formateado siempre con 2 decimales (ej. 14.50)
    return f"{precio_final:.2f}"

# --- RUTAS ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        fecha = request.form.get('fecha_cobro') # Ahora recibe la fecha completa del calendario HTML
        
        nueva_sub = Suscripcion(nombre=nombre, precio=float(precio), fecha_cobro=fecha)
        db.session.add(nueva_sub)
        db.session.commit()
        return redirect(url_for('index'))
    
    suscripciones = Suscripcion.query.all()
    # Enviamos los datos Y la función de colores al HTML
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