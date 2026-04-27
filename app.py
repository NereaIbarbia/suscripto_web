from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text 
from flask_mail import Mail, Message
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.mwaizxcunhxxsryifdnb:Pedorreta123@aws-1-eu-west-1.pooler.supabase.com:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_super_secreta_para_sesiones'
db = SQLAlchemy(app)

TASA_EUR_A_USD = 1.16

# --- CONFIGURACIÓN DE CORREO (GMAIL) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'teamsuscripto@gmail.com'
app.config['MAIL_PASSWORD'] = 'quer ogxz pkpx ybwv'
mail = Mail(app)

TRADUCCIONES = {
    'es': {
        'inicio': 'Inicio', 'calendario': 'Calendario', 'ahorros': 'Ahorros', 'ajustes': 'Ajustes',
        'mis_suscripciones': 'Mis Suscripciones', 'anadir_nueva': '➕ Añadir Nueva',
        'nueva_suscripcion': 'Nueva Suscripción', 'editar_suscripcion': 'Editar Suscripción',
        'servicio': 'Servicio', 'elige_servicio': 'Elige un servicio...', 'otro_personalizado': '✏️ Otro (Personalizado)',
        'nombre_suscripcion': 'Nombre de la suscripción', 'ejemplo_nombre': 'Ej: Gimnasio, ChatGPT...',
        'ciclo': 'Ciclo', 'mensual': 'Mensual', 'anual': 'Anual',
        'precio': 'Precio', 'proximo_cobro': 'Próximo Cobro', 'renovacion_automatica': '🔄 Renovación automática',
        'guardar': 'GUARDAR', 'cobro': 'Cobro', 'editar': '✏️ EDITAR', 'borrar': '🗑️ BORRAR',
        'confirmar_borrar': '¿Seguro que quieres eliminar',
        'sin_suscripciones': 'Aún no tienes suscripciones. Haz clic en el botón de arriba para añadir la primera.',
        'resumen_gastos': 'RESUMEN DE GASTOS', 'gasto_mensual': 'Gasto Mensual Total',
        'datos_actualizados': '✓ Datos actualizados', 'distribucion': 'Distribución por Suscripción',
        'calendario_personalizado': 'Calendario Personalizado',
        'aspectos_graficos': 'ASPECTOS GRÁFICOS Y VISUALES', 'modo_oscuro': 'Modo Oscuro', 'tema_color': 'Tema de Color',
        'funcionalidades': 'FUNCIONALIDADES', 'noti_vencimiento': 'Notificaciones de Vencimiento', 'recordatorios': 'Recordatorios de Ahorro',
        'idioma_region': 'IDIOMA Y REGIÓN', 'idioma': 'Idioma', 'espanol': 'Español', 'ingles': 'Inglés',
        'moneda': 'Moneda', 'otras_configs': 'OTRAS CONFIGURACIONES', 'gestionar_pagos': 'Gestionar Métodos de Pago',
        'cerrar_sesion': 'Cerrar Sesión', 'guardar_cambios': 'Guardar Cambios',
        'euro': 'Euro (€)', 'dolar': 'Dólar ($)',
        'iniciar_sesion': 'Iniciar Sesión', 'registrarse': 'Registrarse', 'crear_cuenta': 'Crear Cuenta',
        'email': 'Tu Email', 'contrasena': 'Tu Contraseña', 'entrar': 'ENTRAR',
        'meses': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        'dias': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        'proyeccion_acumulada': 'Proyección Acumulada (1 Año)',
        'top_gastos': 'Top Mayores Gastos',
        'evalua_gastos': 'Evalúa si realmente usas estos servicios para maximizar tu ahorro.',
        'gasto_acumulado': 'Gasto Acumulado',
        'mes_texto': 'Mes',
        'por_mes': '/mes',
        'prueba_gratuita': '🎁 Tiene Prueba Gratuita (Free Trial)',
        'duracion_prueba': 'Duración de la prueba',
        'dias_7': '7 Días',
        'dias_14': '14 Días',
        'mes_1': '1 Mes'
    },
    'en': {
        'inicio': 'Home', 'calendario': 'Calendar', 'ahorros': 'Savings', 'ajustes': 'Settings',
        'mis_suscripciones': 'My Subscriptions', 'anadir_nueva': '➕ Add New',
        'nueva_suscripcion': 'New Subscription', 'editar_suscripcion': 'Edit Subscription',
        'servicio': 'Service', 'elige_servicio': 'Choose a service...', 'otro_personalizado': '✏️ Other (Custom)',
        'nombre_suscripcion': 'Subscription Name', 'ejemplo_nombre': 'Ex: Gym, ChatGPT...',
        'ciclo': 'Cycle', 'Mensual' : 'Monthly', 'anual': 'Yearly',
        'precio': 'Price', 'proximo_cobro': 'Next Billing', 'renovacion_automatica': '🔄 Auto-renewal',
        'guardar': 'SAVE', 'cobro': 'Billing', 'editar': '✏️ EDIT', 'borrar': '🗑️ DELETE',
        'confirmar_borrar': 'Are you sure you want to delete',
        'sin_suscripciones': 'You have no subscriptions yet. Click the button above to add your first one.',
        'resumen_gastos': 'EXPENSE SUMMARY', 'gasto_mensual': 'Total Monthly Expense',
        'datos_actualizados': '✓ Data updated', 'distribucion': 'Subscription Distribution',
        'calendario_personalizado': 'Custom Calendar',
        'aspectos_graficos': 'GRAPHICS AND VISUALS', 'modo_oscuro': 'Dark Mode', 'tema_color': 'Color Theme',
        'funcionalidades': 'FEATURES', 'noti_vencimiento': 'Expiration Notifications', 'recordatorios': 'Savings Reminders',
        'idioma_region': 'LANGUAGE AND REGION', 'idioma': 'Language', 'espanol': 'Spanish', 'ingles': 'English',
        'moneda': 'Currency', 'otras_configs': 'OTHER SETTINGS', 'gestionar_pagos': 'Manage Payment Methods',
        'cerrar_sesion': 'Log Out', 'guardar_cambios': 'Save Changes',
        'euro': 'Euro (€)', 'dolar': 'Dollar ($)',
        'iniciar_sesion': 'Log In', 'registrarse': 'Sign Up', 'crear_cuenta': 'Create Account',
        'email': 'Your Email', 'contrasena': 'Your Password', 'entrar': 'ENTER',
        'meses': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'dias': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'proyeccion_acumulada': 'Accumulated Projection (1 Year)',
        'top_gastos': 'Top Expenses',
        'evalua_gastos': 'Evaluate if you really use these services to maximize your savings.',
        'gasto_acumulado': 'Accumulated Expense',
        'mes_texto': 'Month',
        'por_mes': '/mo',
        'prueba_gratuita': '🎁 Has Free Trial',
        'duracion_prueba': 'Trial Duration',
        'dias_7': '7 Days',
        'dias_14': '14 Days',
        'mes_1': '1 Month'
    }
}

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    suscripciones = db.relationship('Suscripcion', backref='dueño', lazy=True)

class Suscripcion(db.Model):
    __tablename__ = 'suscripcion_privada'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_cobro = db.Column(db.String(20), nullable=False) 
    ciclo = db.Column(db.String(20), nullable=False, default="Mensual") 
    autorenovacion = db.Column(db.Boolean, default=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

with app.app_context():
    db.create_all()

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
    modo_oscuro = session.get('modo_oscuro', False)
    return dict(moneda=moneda_actual, textos=textos, modo_oscuro=modo_oscuro)

@app.template_filter('convertir_precio')
def convertir_precio(precio_base):
    try:
        precio_base = float(precio_base)
    except (ValueError, TypeError):
        precio_base = 0.0
    moneda_actual = session.get('moneda', '€')
    if moneda_actual == '$':
        precio_final = precio_base * TASA_EUR_A_USD
    else:
        precio_final = precio_base
    return f"{precio_final:.2f}"

# --- FUNCIÓN MÁGICA PARA FREE TRIALS ---
def actualizar_pruebas(usuario_id):
    """Comprueba si alguna prueba gratuita ya ha caducado y la pasa a pago normal"""
    hoy = datetime.now().strftime('%Y-%m-%d')
    subs = Suscripcion.query.filter_by(usuario_id=usuario_id).all()
    cambios = False
    for sub in subs:
        if sub.ciclo.startswith('Prueba ') and sub.fecha_cobro <= hoy:
            sub.ciclo = sub.ciclo.replace('Prueba ', '')
            cambios = True
    if cambios:
        db.session.commit()

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if Usuario.query.filter_by(email=email).first():
            return "El email ya existe. <a href='/login'>Inicia sesión</a>."
        nuevo_usuario = Usuario(email=email, password=generate_password_hash(password))
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password, password):
            session['usuario_id'] = usuario.id
            return redirect(url_for('index'))
        else:
            return "Email o contraseña incorrectos. <a href='/login'>Intentar de nuevo</a>."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))

# --- RUTAS PROTEGIDAS ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    mi_user_id = session['usuario_id']
    
    actualizar_pruebas(mi_user_id)

    if request.method == 'POST':
        sub_id = request.form.get('sub_id')
        nombre = request.form.get('nombre_final') 
        precio = request.form.get('precio')
        fecha = request.form.get('fecha_cobro')
        ciclo = request.form.get('ciclo') 
        es_auto = request.form.get('autorenovacion') == 'on'
        es_prueba = request.form.get('es_prueba') == 'true'
        
        if sub_id:
            sub_existente = Suscripcion.query.filter_by(id=int(sub_id), usuario_id=mi_user_id).first()
            if sub_existente:
                sub_existente.nombre = nombre
                sub_existente.precio = float(precio)
                sub_existente.fecha_cobro = fecha
                sub_existente.ciclo = ciclo
                sub_existente.autorenovacion = es_auto
        else:
            ciclo_final = f"Prueba {ciclo}" if es_prueba else ciclo
            nueva_sub = Suscripcion(nombre=nombre, precio=float(precio), fecha_cobro=fecha, ciclo=ciclo_final, autorenovacion=es_auto, usuario_id=mi_user_id)
            db.session.add(nueva_sub)
            
        db.session.commit()
        return redirect(url_for('index'))
    
    suscripciones = Suscripcion.query.filter_by(usuario_id=mi_user_id).all()
    return render_template('index.html', suscripciones=suscripciones, get_color=obtener_color)

@app.route('/borrar/<int:id>')
def borrar(id):
    if 'usuario_id' not in session: return redirect(url_for('login'))
    sub = Suscripcion.query.filter_by(id=id, usuario_id=session['usuario_id']).first_or_404()
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/calendario')
def calendario():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    actualizar_pruebas(session['usuario_id'])
    suscripciones = Suscripcion.query.filter_by(usuario_id=session['usuario_id']).all()
    return render_template('calendario.html', suscripciones=suscripciones, get_color=obtener_color)

@app.route('/ahorro')
def ahorro():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    actualizar_pruebas(session['usuario_id'])
    suscripciones = Suscripcion.query.filter_by(usuario_id=session['usuario_id']).all()
    
    total_mensual = sum(
        0 if sub.ciclo.startswith('Prueba') else (sub.precio if sub.ciclo == 'Mensual' else sub.precio / 12) 
        for sub in suscripciones
    )
    
    return render_template('ahorro.html', suscripciones=suscripciones, total_gastado=total_mensual, get_color=obtener_color)

@app.route('/ajustes', methods=['GET', 'POST'])
def ajustes():
    if 'usuario_id' not in session: return redirect(url_for('login'))
    lang = request.args.get('lang')
    if lang in TRADUCCIONES:
        session['idioma'] = lang 
    if request.method == 'POST':
        nueva_moneda = request.form.get('moneda')
        if nueva_moneda:
            session['moneda'] = nueva_moneda 
        modo_oscuro_form = request.form.get('modo_oscuro')
        session['modo_oscuro'] = (modo_oscuro_form == 'on')
        return redirect(url_for('ajustes')) 
    return render_template('ajustes.html')

def enviar_recordatorios():
    with app.app_context():
        hoy = datetime.now()
        manana = (hoy + timedelta(days=1)).strftime('%Y-%m-%d')
        pendientes = Suscripcion.query.filter_by(fecha_cobro=manana).all()
        emails_enviados = 0
        for sub in pendientes:
            usuario = Usuario.query.get(sub.usuario_id)
            if usuario and usuario.email:
                try:
                    msg = Message(
                        subject=f"🔔 Recordatorio Suscripto: {sub.nombre}",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[usuario.email]
                    )
                    msg.body = f"¡Hola!\n\nTe avisamos de que tu suscripción a '{sub.nombre}' se renovará mañana ({manana}) por un importe de {sub.precio}€.\n\n¡Que tengas un buen día!"
                    mail.send(msg)
                    emails_enviados += 1
                except Exception as e:
                    print(f"Error enviando a {usuario.email}: {e}")
        return f"Proceso finalizado. Correos enviados: {emails_enviados}"

@app.route('/test-notificaciones')
def test_notificaciones():
    resultado = enviar_recordatorios()
    return f"<h1>Estado del envío:</h1><p>{resultado}</p>"

if __name__ == '__main__':
    app.run(debug=True)