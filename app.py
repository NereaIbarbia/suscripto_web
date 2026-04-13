from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.mwaizxcunhxxsryifdnb:Pedorreta123@aws-1-eu-west-1.pooler.supabase.com:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_super_secreta_para_sesiones'
db = SQLAlchemy(app)

# Tasa de conversión de Euros a Dólares
TASA_EUR_A_USD = 1.16

# Diccionario completo de traducciones
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
        'meses': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        'dias': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    },
    'en': {
        'inicio': 'Home', 'calendario': 'Calendar', 'ahorros': 'Savings', 'ajustes': 'Settings',
        'mis_suscripciones': 'My Subscriptions', 'anadir_nueva': '➕ Add New',
        'nueva_suscripcion': 'New Subscription', 'editar_suscripcion': 'Edit Subscription',
        'servicio': 'Service', 'elige_servicio': 'Choose a service...', 'otro_personalizado': '✏️ Other (Custom)',
        'nombre_suscripcion': 'Subscription Name', 'ejemplo_nombre': 'Ex: Gym, ChatGPT...',
        'ciclo': 'Cycle', 'mensual': 'Monthly', 'anual': 'Yearly',
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
        'meses': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'dias': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    }
}

class Suscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_cobro = db.Column(db.String(20), nullable=False) 
    ciclo = db.Column(db.String(20), nullable=False, default="Mensual") 
    autorenovacion = db.Column(db.Boolean, default=True)

with app.app_context():
    db.create_all()
    try:
        db.session.execute(text("ALTER TABLE suscripcion ADD COLUMN ciclo VARCHAR(20) DEFAULT 'Mensual';"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE suscripcion ADD COLUMN autorenovacion BOOLEAN DEFAULT TRUE;"))
        db.session.commit()
    except Exception:
        db.session.rollback()

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

# Filtro para convertir moneda de euros a dólares
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sub_id = request.form.get('sub_id')
        nombre = request.form.get('nombre_final') 
        precio = request.form.get('precio')
        fecha = request.form.get('fecha_cobro')
        ciclo = request.form.get('ciclo') 
        es_auto = request.form.get('autorenovacion') == 'on'
        
        if sub_id:
            sub_existente = Suscripcion.query.get(int(sub_id))
            if sub_existente:
                sub_existente.nombre = nombre
                sub_existente.precio = float(precio)
                sub_existente.fecha_cobro = fecha
                sub_existente.ciclo = ciclo
                sub_existente.autorenovacion = es_auto
        else:
            nueva_sub = Suscripcion(nombre=nombre, precio=float(precio), fecha_cobro=fecha, ciclo=ciclo, autorenovacion=es_auto)
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
    total_mensual = sum(sub.precio if sub.ciclo == 'Mensual' else (sub.precio / 12) for sub in suscripciones)
    return render_template('ahorro.html', suscripciones=suscripciones, total_gastado=total_mensual, get_color=obtener_color)

@app.route('/ajustes', methods=['GET', 'POST'])
def ajustes():
    lang = request.args.get('lang')
    if lang in TRADUCCIONES:
        session['idioma'] = lang 
        
    if request.method == 'POST':
        nueva_moneda = request.form.get('moneda')
        if nueva_moneda:
            session['moneda'] = nueva_moneda 
            
        modo_oscuro_form = request.form.get('modo_oscuro')
        if modo_oscuro_form == 'on':
            session['modo_oscuro'] = True
        else:
            session['modo_oscuro'] = False
        
        return redirect(url_for('ajustes')) 
    
    return render_template('ajustes.html')

if __name__ == '__main__':
    app.run(debug=True)