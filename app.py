from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Configuramos una base de datos SQL sencilla (SQLite) [cite: 157]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suscripto.db'
db = SQLAlchemy(app)

# Definimos qué datos queremos guardar de cada suscripción [cite: 215]
class Suscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.String(20)) # Formato simple

# Ruta principal: Ver suscripciones 
@app.route('/')
def index():
    suscripciones = Suscripcion.query.all()
    total = sum(s.precio for s in suscripciones) # Suma total [cite: 31]
    return render_template('index.html', lista=suscripciones, total=total)

# Ruta para añadir nuevas [cite: 32, 226]
@app.route('/add', methods=['POST'])
def add():
    nueva = Suscripcion(
        nombre=request.form['nombre'],
        precio=float(request.form['precio']),
        fecha_pago=request.form['fecha']
    )
    db.session.add(nueva)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea la base de datos automáticamente
    app.run(debug=True)