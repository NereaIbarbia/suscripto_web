from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import calendar

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suscripto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE DATOS ---
class Suscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    # Se asume que guardas solo el día (ej: "15") o una fecha que manejas luego
    fecha_pago = db.Column(db.String(20)) 

# --- RUTA 1: INICIO / DASHBOARD ---
@app.route('/')
def index():
    # Aseguramos que las tablas existan al entrar
    db.create_all()
    
    suscripciones = Suscripcion.query.all()
    total = sum(s.precio for s in suscripciones)
    return render_template('index.html', lista=suscripciones, total=total, active_page='index')

# --- RUTA 2: AÑADIR SUSCRIPCIÓN ---
@app.route('/add', methods=['POST'])
def add():
    try:
        nueva = Suscripcion(
            nombre=request.form['nombre'],
            precio=float(request.form['precio']),
            fecha_pago=request.form['fecha']
        )
        db.session.add(nueva)
        db.session.commit()
    except Exception as e:
        print(f"Error al añadir: {e}")
    return redirect(url_for('index'))

# --- RUTA 3: CALENDARIO ---
@app.route('/calendario')
def calendario():
    ahora = datetime.now()
    year = ahora.year
    month = ahora.month
    
    # Generar la matriz del calendario
    cal = calendar.monthcalendar(year, month)
    
    # Nombres de meses en español
    nombres_meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    nombre_mes = nombres_meses.get(month, "Mes Desconocido")
    
    suscripciones = Suscripcion.query.all()
    
    # Organizar eventos por día
    eventos = {}
    for s in suscripciones:
        if s.fecha_pago:
            try:
                # Intentamos convertir a entero por si guardaste solo el día "5"
                dia = int(s.fecha_pago)
                if dia not in eventos:
                    eventos[dia] = []
                eventos[dia].append(s)
            except ValueError:
                # Si la fecha no es un número simple, se ignora para evitar error 500
                pass

    return render_template('calendario.html', 
                           calendario=cal, 
                           mes=nombre_mes, 
                           anio=year, 
                           eventos=eventos, 
                           active_page='calendario')

# --- RUTA 4: AHORRO ---
@app.route('/ahorro')
def ahorro():
    suscripciones = Suscripcion.query.all()
    total = sum(s.precio for s in suscripciones)
    
    # Listas para pasar a las gráficas (Chart.js u otra librería)
    labels = [s.nombre for s in suscripciones]
    data = [s.precio for s in suscripciones]
    
    return render_template('ahorro.html', 
                           total=total, 
                           labels=labels, 
                           data=data,
                           active_page='ahorro')

# --- RUTA 5: AJUSTES ---
@app.route('/ajustes')
def ajustes():
    return render_template('ajustes.html', active_page='ajustes')

# --- ARRANQUE DE LA APP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)