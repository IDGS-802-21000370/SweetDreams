from datetime import datetime
import matplotlib.pyplot as plt
import base64
import io
from flask import Flask, request, render_template, Response, redirect, url_for
import forms
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import flash
from models import db
from models import Usuario, Venta, DetalleVentas, Galleta, TipoVenta
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombreUsuario = request.form['nombreUsuario']
        contrasenia = request.form['contrasenia']
        user = Usuario.query.filter_by(nombreUsario=nombreUsuario, contrasenia=contrasenia).first()
        if user:
            login_user(Usuario)
            return redirect(url_for('admin'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(app, name='Microblog', template_mode='bootstrap3')
admin.add_view(MyModelView(Usuario, db.session))

@app.route("/usuario", methods=["GET", "POST"])
def usuario():
    usuarioForm = forms.UsuarioForm(request.form)
    usuarios = Usuario.query.all()
    if request.method == 'POST':
        if 'registrar' in request.form:
            nuevo_usuario = Usuario(
                nombre=usuarioForm.nombre.data,
                nombreUsuario=usuarioForm.nombreUsuario.data,
                contrasenia=usuarioForm.contrasenia.data,
                puesto=usuarioForm.puesto.data,
                rol=usuarioForm.rol.data
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for('usuario'))
            
        elif 'accion' in request.form:
            accion, usuario_id_str = request.form['accion'].split('_', 1)
            usuario_id = int(usuario_id_str)
            if accion == 'editar':
                usuario_editar = Usuario.query.get_or_404(usuario_id)
                
                usuarioForm.id_usuario.data=usuario_editar.id_usuario
                usuarioForm.nombre.data = usuario_editar.nombre
                usuarioForm.nombreUsuario.data = usuario_editar.nombreUsuario
                usuarioForm.contrasenia.data = usuario_editar.contrasenia
                usuarioForm.puesto.data = usuario_editar.puesto
                usuarioForm.rol.data = usuario_editar.rol
                return render_template("usuario.html", formUsuario=usuarioForm, usuarios=usuarios)
        elif 'actualizar' in request.form:
            nombre_usuario = usuarioForm.nombreUsuario.data
            usuario_actualizar = Usuario.query.filter_by(nombreUsuario=nombre_usuario).first()
            if usuario_actualizar:
                usuario_actualizar.nombre = usuarioForm.nombre.data
                usuario_actualizar.nombreUsuario = usuarioForm.nombreUsuario.data
                usuario_actualizar.contrasenia = usuarioForm.contrasenia.data
                usuario_actualizar.puesto = usuarioForm.puesto.data
                usuario_actualizar.rol = usuarioForm.rol.data
                db.session.commit()
                
            return redirect(url_for('usuario'))
        elif 'eliminar' in request.form:
            id_usuario = int(request.form['eliminar'])
            usuario_eliminar = Usuario.query.get_or_404(id_usuario)
            db.session.delete(usuario_eliminar)
            db.session.commit()
            return redirect(url_for('usuario'))
    return render_template("usuario.html", formUsuario=usuarioForm, usuarios=usuarios)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    ventas_diarias = calcular_ventas_diarias()
    plot_url_ventas_diarias, plot_url_productos_vendidos, plot_url_ventas_tipo = generar_grafico_ventas_diarias(ventas_diarias)
    return render_template('dashboard.html', plot_url_ventas_diarias=plot_url_ventas_diarias, plot_url_productos_vendidos=plot_url_productos_vendidos, plot_url_ventas_tipo=plot_url_ventas_tipo)

def calcular_ventas_diarias():
    fecha_actual = datetime.datetime.now().date()
    ventas_diarias = db.session.query(
        func.date(Venta.fecha_creacion).label('fecha'),
        func.sum(Venta.total).label('total')
    ).filter(
        func.date(Venta.fecha_creacion) == fecha_actual
    ).group_by(
        func.date(Venta.fecha_creacion)
    ).all()

    return ventas_diarias

def generar_grafico_ventas_diarias(ventas_diarias):
    labels = [venta.fecha.strftime('%Y-%m-%d') for venta in ventas_diarias]
    values = [venta.total for venta in ventas_diarias]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.xlabel('Fecha')
    plt.ylabel('Total Vendido')
    plt.title('Ventas Diarias')
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_stream_ventas_diarias = io.BytesIO()
    plt.savefig(image_stream_ventas_diarias, format='png')
    image_stream_ventas_diarias.seek(0)
    plt.close()

    detalles_ventas = db.session.query(
        DetalleVentas.galleta_id_galleta,
        func.sum(DetalleVentas.cantidad).label('total_vendido')
    ).group_by(
        DetalleVentas.galleta_id_galleta
    ).all()

    ventas_por_producto = {detalle.galleta_id_galleta: detalle.total_vendido for detalle in detalles_ventas}

    productos_mas_vendidos = sorted(
        ventas_por_producto.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]

    nombres_productos_mas_vendidos = [Galleta.query.get(id_galleta).nombre for id_galleta, _ in productos_mas_vendidos]
    cantidades_productos_mas_vendidos = [cantidad for _, cantidad in productos_mas_vendidos]

    plt.figure(figsize=(10, 6))
    plt.bar(nombres_productos_mas_vendidos, cantidades_productos_mas_vendidos)
    plt.xlabel('Producto')
    plt.ylabel('Cantidad Vendida')
    plt.title('Productos Más Vendidos')
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_stream_productos_vendidos = io.BytesIO()
    plt.savefig(image_stream_productos_vendidos, format='png')
    image_stream_productos_vendidos.seek(0)
    plt.close()

    detalles_ventas_tipos = db.session.query(
        DetalleVentas.galleta_id_galleta,
        DetalleVentas.tipoventa_id_tipoVenta,
        func.sum(DetalleVentas.cantidad).label('total_vendido')
    ).group_by(
        DetalleVentas.galleta_id_galleta,
        DetalleVentas.tipoventa_id_tipoVenta
    ).all()

    ventas_por_tipo = {}
    for detalle in detalles_ventas_tipos:
        galleta_id = detalle.galleta_id_galleta
        tipo_venta_id = detalle.tipoventa_id_tipoVenta
        tipo_venta_nombre = TipoVenta.query.get(tipo_venta_id).descripcion
        cantidad = detalle.total_vendido
        if galleta_id not in ventas_por_tipo:
            ventas_por_tipo[galleta_id] = {}
        ventas_por_tipo[galleta_id][tipo_venta_nombre] = cantidad

    nombres_galletas = [Galleta.query.get(id_galleta).nombre for id_galleta in ventas_por_tipo.keys()]
    piezas = [ventas.get('Pieza', 0) for ventas in ventas_por_tipo.values()]
    cajas = [ventas.get('Caja', 0) for ventas in ventas_por_tipo.values()]
    granajes = [ventas.get('Granaje', 0) for ventas in ventas_por_tipo.values()]

    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    indices = range(len(nombres_galletas))
    
    plt.bar(indices, piezas, bar_width, label='Pieza')
    plt.bar(indices, cajas, bar_width, bottom=piezas, label='Caja')
    plt.bar(indices, granajes, bar_width, bottom=[i+j for i,j in zip(piezas, cajas)], label='Granaje')
    
    plt.xlabel('Galleta')
    plt.ylabel('Cantidad Vendida')
    plt.title('Ventas por Tipo de Galleta')
    plt.xticks(indices, nombres_galletas, rotation=45)
    plt.legend()
    plt.tight_layout()

    image_stream_ventas_tipo = io.BytesIO()
    plt.savefig(image_stream_ventas_tipo, format='png')
    image_stream_ventas_tipo.seek(0)
    plt.close()

    image_base64_ventas_diarias = base64.b64encode(image_stream_ventas_diarias.getvalue()).decode('utf-8')
    image_base64_productos_vendidos = base64.b64encode(image_stream_productos_vendidos.getvalue()).decode('utf-8')
    image_base64_ventas_tipo = base64.b64encode(image_stream_ventas_tipo.getvalue()).decode('utf-8')

    return image_base64_ventas_diarias, image_base64_productos_vendidos, image_base64_ventas_tipo

@app.route("/galletas", methods=["GET", "POST"])
def galletas():
    if request.method=="POST":
        print("holad")
    return render_template("galletas.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all() 
    app.run(debug=True)


