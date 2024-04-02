from datetime import date
import os
import datetime
import time
from datetime import datetime
import matplotlib.pyplot as plt
import base64
import io
from flask import Flask, request, render_template, Response, redirect, url_for
import forms
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import flash
from models import DetalleReceta, Galleta, MateriasPrimas, Receta, TipoMedidasMaterialPrimas, db
from models import db, Proveedor, Compra, DetalleCompra
import proveedor
from models import db
from produccionGalletas import Guardar
from models import Usuario, Venta, DetalleVentas, Galleta, TipoVenta
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()
MPrima = []
MPrimaTexto = []

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

menu_items = []

@app.route("/ventas", methods=["GET", "POST"])
def ventas():
    galletas=Galleta.query.all()
    if request.method=="POST":
        if 'agregarPieza' in request.form:
            galletaAgregada=Galleta.query.filter_by(id_galleta=int(request.form['agregarPieza'])).first()
            id_galleta = galletaAgregada.id_galleta
            nombre = galletaAgregada.nombre
            precio = galletaAgregada.precio
            encontrado = False
            for item in menu_items:
                if item['id_galleta'] == id_galleta:
                    item['precio'] += precio
                    encontrado = True
                    break
            
            if not encontrado:
                menu_items.append({"id_galleta": id_galleta, "nombre": nombre, "precio": precio})
        return render_template('ventas.html', galletas=galletas, menu_items=menu_items)
    return render_template('ventas.html', galletas=galletas)

@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    tipo_medida_map = {
        '1': 'Gramos',
        '2': 'Piezas',
        '3': 'Mililitros',
        '4': 'Costales'
    }
    galletas=Galleta.query.all()
    materiasPrimas=MateriasPrimas.query.all()
    #tipoMedida = tipo_medida_map.get(tipoMedida, '')
    if request.method=="POST":
        if 'mandarMerma' in request.form:
            print('se mando a merma')
    return render_template("inventario.html", galletas=galletas, materiasPrimas=materiasPrimas)

contador_recetas = 0

@app.route("/recetas", methods=["GET", "POST"])
def recetas():
    formReceta=forms.RecetaForm(request.form)
    materiasPrimas=MateriasPrimas.query.all()
    cargarMateriasPrimas=[]
    tipo_medida_map = {
        '1': 'Gramos',
        '2': 'Piezas',
        '3': 'Mililitros',
        '4': 'Costales'
    }

    tipoMedidaMateriaPrima=TipoMedidasMaterialPrimas.query.all()
    if request.method=="POST":
        ingrediente = request.form['materiasPrimas']
        cantidad = request.form['cantidad']
        tipoMedida = request.form['tipoMedidaMateriaPrima']

        if 'registrar' in request.form:
            materiaPrima = MateriasPrimas.query.filter_by(id_materiaPrima=int(ingrediente)).all()
            ingrediente = materiaPrima[0].nombre
            tipoMedida = tipo_medida_map.get(tipoMedida, '')
            global contador_recetas
            contador_recetas += 1
            with open("recetas.txt", "a", encoding="utf-8") as file:
                file.write(f"id_catReceta: {contador_recetas}, ingrediente: {ingrediente}, cantidad: {cantidad}, tipoMedida: {tipoMedida}\n")
            
            with open("recetas.txt", "r",  encoding="utf-8") as file:
                    recetas = file.readlines()
            receta_formateada = []
            for dato in recetas:
                partes = dato.strip().split(", ")
                receta = {}
                for parte in partes:
                    if ": " in parte:
                        clave, valor = parte.split(": ", 1)
                        receta[clave] = valor
                receta_formateada.append(receta)
            return render_template("recetas.html", formReceta = formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, receta=receta_formateada)
        elif 'eliminar' in request.form:
            id = int(request.form['eliminar'])
            with open("recetas.txt", "r", encoding="utf-8") as file:
                lineas = file.readlines()

            with open("recetas.txt", "w", encoding="utf-8") as file:
                for linea in lineas:
                    partes = linea.strip().split(", ")
                    for parte in partes:
                        if "id_catReceta: " in parte:
                            receta_id = int(parte.split(": ")[1])
                            if receta_id == id:
                                break
                    else:
                        file.write(linea)
            with open("recetas.txt", "r",  encoding="utf-8") as file:
                recetas = file.readlines()
            if len(recetas) != 0:
                receta_formateada = []
                for dato in recetas:
                    partes = dato.strip().split(", ")
                    receta = {}
                    for parte in partes:
                        if ": " in parte:
                            clave, valor = parte.split(": ", 1)
                            receta[clave] = valor
                    receta_formateada.append(receta)
                return render_template("recetas.html", formReceta = formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, receta=receta_formateada)
        elif 'insertar' in request.form:
            formReceta = forms.RecetaForm(request.form)
            if request.form['id_receta'] != '' and request.form['id_receta'] != 'None':
                return render_template("recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal=True, id_re=request.form['id_receta'])
            else:
                receta = Receta(nombre=formReceta.nombreReceta.data,
                            descripcion=formReceta.descripcion.data,
                            totalGalletas=int(formReceta.totalGalletas.data),
                            precioTotal=100,
                            fecha_actualiza=datetime.datetime.now())
                db.session.add(receta)
                db.session.commit()
                
                with open("recetas.txt", "r",  encoding="utf-8") as file:
                    recetas = file.readlines()
                if len(recetas) != 0:
                    receta_formateada = []
                    for dato in recetas:
                        partes = dato.strip().split(", ")
                        receta = {}
                        for parte in partes:
                            if ": " in parte:
                                clave, valor = parte.split(": ", 1)
                                receta[clave] = valor
                        receta_formateada.append(receta)
                receta = Receta.query.order_by(Receta.id_receta.desc()).limit(1).first()
                for r in range(len(receta_formateada)):
                    materiasPrimas = MateriasPrimas.query.filter_by(nombre=receta_formateada[r]['ingrediente']).all()
                    id_materiaPrima = materiasPrimas[0].id_materiaPrima
                    tipoMedida = TipoMedidasMaterialPrimas.query.filter_by(descripcion=receta_formateada[r]['tipoMedida']).all()
                    id_tipoMedida = tipoMedida[0].id_medida

                    detalleReceta = DetalleReceta(cantidad=receta_formateada[r]['cantidad'],
                                                receta_id_receta=receta.id_receta,
                                                materiasprimas_id_materiaPrima=id_materiaPrima,
                                                tipomedidasmaterialprimas_id_medida=id_tipoMedida)
                    db.session.add(detalleReceta)
                    db.session.commit()
                os.remove("recetas.txt")
                return render_template("recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal=False)
        elif 'cargar' in request.form:
                recetasCargadas=Receta.query.all()
                return render_template("recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, recetasCargadas=recetasCargadas)
        elif 'obtenerModificar' in request.form:
            formReceta=forms.RecetaForm(request.form)
            cargarReceta = Receta.query.filter_by(id_receta=int(request.form['obtenerModificar'])).all()
            formReceta.id_receta.data = cargarReceta[0].id_receta
            formReceta.nombreReceta.data = cargarReceta[0].nombre
            formReceta.descripcion.data = cargarReceta[0].descripcion
            formReceta.totalGalletas.data = str(cargarReceta[0].totalGalletas)
            return render_template("recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, cargarReceta=cargarReceta)
        elif 'actualizar' in request.form:
            formReceta=forms.RecetaForm(request.form)
            cargarMateriasPrimas=DetalleReceta.query.filter_by(receta_id_receta=int(formReceta.id_receta.data)).all()
            for mp in cargarMateriasPrimas:
                db.session.delete(mp)
            db.session.commit()

            modificaReceta = Receta.query.filter_by(id_receta=int(formReceta.id_receta.data)).first()
            modificaReceta.nombre = formReceta.nombreReceta.data
            modificaReceta.descripcion = formReceta.descripcion.data
            modificaReceta.totalGalletas = int(formReceta.totalGalletas.data)
            modificaReceta.precioTotal = 100
            modificaReceta.fecha_actualiza = datetime.datetime.now()
            db.session.commit()

            with open("recetas.txt", "r",  encoding="utf-8") as file:
                recetas = file.readlines()
            if len(recetas) != 0:
                receta_formateada = []
                for dato in recetas:
                    partes = dato.strip().split(", ")
                    receta = {}
                    for parte in partes:
                        if ": " in parte:
                            clave, valor = parte.split(": ", 1)
                            receta[clave] = valor
                    receta_formateada.append(receta)
            receta = Receta.query.order_by(Receta.id_receta.desc()).limit(1).first()
            for r in range(len(receta_formateada)):
                materiasPrimas = MateriasPrimas.query.filter_by(nombre=receta_formateada[r]['ingrediente']).all()
                id_materiaPrima = materiasPrimas[0].id_materiaPrima
                tipoMedida = TipoMedidasMaterialPrimas.query.filter_by(descripcion=receta_formateada[r]['tipoMedida']).all()
                id_tipoMedida = tipoMedida[0].id_medida

                detalleReceta = DetalleReceta(cantidad=receta_formateada[r]['cantidad'],
                                              receta_id_receta=formReceta.id_receta.data,
                                              materiasprimas_id_materiaPrima=id_materiaPrima,
                                              tipomedidasmaterialprimas_id_medida=id_tipoMedida)
                db.session.add(detalleReceta)
                db.session.commit()
            os.remove("recetas.txt")
            return render_template("recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, cargarMateriasPrimas=cargarMateriasPrimas)
    return render_template("recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima,  mostrar_modal=False)

@app.route("/mermas", methods=["GET", "POST"])
def mermas():
    if request.method=="POST":
        print("holad")
    return render_template("mermas.html")

@app.route("/proveedores", methods=["GET", "POST"])
def proveedorIndex():
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    
    if request.method == "POST":
        if 'buttonP' in request.form:
            #Alerta para eliminar
            proveedor.eliminarP()
            return redirect(url_for('proveedorIndex'))
        
    return render_template("proveedor/proveedor.html", Proveedor=proveedores)

@app.route("/proveedoresForm", methods=["GET", "POST"])
def prooveedorForm():
    prvdForm=forms.ProveedorForm(request.form)
    if request.method=="POST":
        if request.form['btnPrv'] == "btnRegistrarPrv":
            #Alerta para registrar
            proveedor.indexP()
            return redirect(url_for('proveedorIndex'))
            
    return render_template("proveedor/proveedorForm.html", formProveedor=prvdForm)

@app.route("/proveedoresUpdate", methods=["GET", "POST"])
def prooveedorUpdate():
    prvdForm=forms.getProveedor(request.form)
    if request.method=='GET':
        id=request.args.get('id')
        prvdA=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
        prvdForm.id.data=request.args.get('id')
        prvdForm.nombreEmpresa.data=prvdA.nombreEmpresa
        prvdForm.direccion.data=prvdA.direccion
        prvdForm.contacto.data=prvdA.contacto
    if request.method=="POST":
        #Alerta para editar
        id=prvdForm.id.data
        prvd=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
        prvd.nombreEmpresa=prvdForm.nombreEmpresa.data
        prvd.direccion=prvdForm.direccion.data
        prvd.contacto=prvdForm.contacto.data
        db.session.add(prvd)
        db.session.commit()
        return redirect(url_for('proveedorIndex'))
    return render_template("proveedor/proveedorM.html", formProveedor=prvdForm)

@app.route("/compras", methods=["GET", "POST"])
def compraIndex():
    compras = Compra.query.all()
        
    return render_template("compra/compra.html", Compra=compras)

@app.route("/detalleCompra", methods=["GET", "POST"])
def detalleCompraIndex():
    if request.method=='GET':
        id=request.args.get('id')
        dCompras = DetalleCompra.query.filter_by(compra_id_compra=id).all()
        
    return render_template("compra/detalleCompra.html", dCompra=dCompras)

@app.route("/compraForm", methods=["GET", "POST"])
def compraForm():
    crpForm=forms.CompraForm(request.form)
    global MPrima
    global MPrimaTexto
    
    if request.method=="POST":
        if request.form['buttonMP'] == "btnAgregarMP":
            cantidad=crpForm.cantidad.data
            tipoMP_id = crpForm.idTipoMedida.data
            tipoMP_valor = dict(crpForm.idTipoMedida.choices).get(tipoMP_id)
            materiaprima_id = crpForm.idMateriaPrima.data
            materiaprima_valor = dict(crpForm.idMateriaPrima.choices).get(materiaprima_id)
            prvd_id = crpForm.idProveedor.data
            prvd_valor = dict(crpForm.idProveedor.choices).get(prvd_id)
            print(tipoMP_valor)
            MPrima.append({ 
                           'cantidad': cantidad, 
                           'tipoMP':tipoMP_id, 
                           'materiaprima': materiaprima_id, 
                           'prvd':prvd_id
                           }
            )
            MPrimaTexto.append({ 
                           'cantidad': cantidad, 
                           'tipoMP':tipoMP_valor, 
                           'materiaprima': materiaprima_valor, 
                           'prvd':prvd_valor
                           }
            )

        if request.form['buttonMP'] == "btnQuitarMP":
            indexEliminar = request.form.getlist('eliminar[]')
            indexEliminar = [int(index) for index in indexEliminar]
            MPrima = [materiap for i, materiap in enumerate(MPrima, 1) if i not in indexEliminar]
        
        if request.form['buttonMP'] == "btnLimpiarMP":
            MPrima.clear()

        #Alerta para Registrar
        if request.form['buttonMP'] == "btnRegistrarMP":
            #tabla compra
            prvd=Compra(totalCompra=crpForm.totalCompra.data, fecha_actualiza = crpForm.fecha_actualiza.data, usuario_id_usuario = 1)
                #Cambiar id_usuario por id del usuario loggeado
            db.session.add(prvd)
            db.session.commit()
            
            #tabla detalle compra
            idCompra = db.session.query(db.func.max(Compra.id_compra)).scalar()
            for elemento in MPrima:
                cantidad = elemento['cantidad']
                tipoMP_id = elemento['tipoMP']
                materiaprima_id = elemento['materiaprima']
                prvd_id = elemento['prvd']
        
                detalle = DetalleCompra(cantidad=cantidad, tipomedidasmaterialprimas_id_medida=tipoMP_id, 
                                        compra_id_compra=idCompra, materiasprimas_id_materiaPrima=materiaprima_id, 
                                        proveedor_id_proveedor=prvd_id)
        
                db.session.add(detalle)
                db.session.commit()
            MPrima.clear()
            MPrimaTexto.clear()

    return render_template("compra/compraForm.html", formCompra=crpForm, MPrima=MPrimaTexto)
        
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404
@app.route("/produccionGalleta", methods=["GET", "POST"])
def produccionGalletas():
    galletas_en_preparacion = []
    galletas_preparadas = []

    if request.method == "POST":
        galleta_seleccionada = request.form["galleta"]
        Guardar.galletasenpreparacion(galleta_seleccionada)
        #Guardar.mandarmostrador()
    with open("galletas_en_preparacion.txt", "r") as file:
        galletas_en_preparacion = file.readlines()
    
    with open("galletas_preparadas.txt", "r") as file:
        galletas_preparadas = file.readlines()
          
    return render_template("produccionGalleta.html", galletas_en_preparacion=galletas_en_preparacion, galletas_preparadas=galletas_preparadas)
@app.route("/enviarMostrador", methods=["POST"])
def enviarMostrador():
    Guardar.mandar_mostrador(app)
   
    return  render_template("produccionGalleta.html")
if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all() 
    app.run(debug=True)


