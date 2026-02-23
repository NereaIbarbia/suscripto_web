from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos (se creará un archivo llamado suscripciones.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suscripciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------------
# MODELO DE BASE DE DATOS
# ---------------------------------------------------------
class Suscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_cobro = db.Column(db.String(20), nullable=False)

# Esto crea el archivo de la base de datos la primera vez que ejecutas el programa
with app.app_context():
    db.create_all()

# ---------------------------------------------------------
# RUTAS DE LA PÁGINA WEB
# ---------------------------------------------------------

# RUTA PRINCIPAL (Inicio) -> Ojo aquí al methods=['GET', 'POST']
@app.route('/', methods=['GET', 'POST'])
def index():
    # Si el usuario le ha dado al botón de "AÑADIR NUEVA" (POST)
    if request.method == 'POST':
        # 1. Cogemos los datos que ha escrito en el formulario
        nombre_sub = request.form['nombre']
        precio_sub = request.form['precio']
        fecha_sub = request.form['fecha_cobro']
        
        # 2. Preparamos los datos para la base de datos
        nueva_suscripcion = Suscripcion(
            nombre=nombre_sub, 
            precio=float(precio_sub), 
            fecha_cobro=fecha_sub
        )
        
        # 3. Lo guardamos permanentemente
        db.session.add(nueva_suscripcion)
        db.session.commit()
        
        # 4. Recargamos la página de inicio para que aparezca en la lista
        return redirect(url_for('index'))
    
    # Si el usuario solo está entrando a la web normalmente (GET)
    # 1. Pedimos a la base de datos TODAS las suscripciones guardadas
    suscripciones = Suscripcion.query.all()
    
    # 2. Calculamos el dinero total gastado y lo redondeamos a 2 decimales
    total = sum(sub.precio for sub in suscripciones)
    total_redondeado = round(total, 2)
    
    # 3. Enviamos los datos al diseño HTML
    return render_template('index.html', suscripciones=suscripciones, total_gastado=total_redondeado)

# RUTA CALENDARIO
@app.route('/calendario')
def calendario():
    return render_template('calendario.html')

# RUTA AHORRO
@app.route('/ahorro')
def ahorro():
    return render_template('ahorro.html')

# RUTA AJUSTES
@app.route('/ajustes')
def ajustes():
    return render_template('ajustes.html')

# ---------------------------------------------------------
# INICIO DEL SERVIDOR
# ---------------------------------------------------------
if __name__ == '__main__':
    # debug=True hace que los cambios se actualicen solos sin tener que apagar el servidor
    app.run(debug=True)