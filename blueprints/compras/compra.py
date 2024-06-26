from flask import Blueprint, render_template, request, url_for, redirect, flash
import blueprints.forms as forms
from blueprints.models import Compra, DetalleCompra, Caja, CajaRetiro, DetalleMateriaPrima, MateriasPrimas, TipoMedidasMaterialPrimas, DetalleProveedorMateria, Proveedor, db
from datetime import datetime
from functools import wraps
from flask_login import current_user

compra_blueprint = Blueprint("compras", __name__, template_folder="templates")
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

MPrima = []
MPrimaTexto = []
def obtener_mp_por_proveedor():
    mp_por_proveedor = {}
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    for proveedor in proveedores:
        mp_por_proveedor[proveedor.id_proveedor] = []
        materias_primas = DetalleProveedorMateria.query.filter_by(proveedor_id_proveedor=proveedor.id_proveedor, estatus=1).all()
        for mp in materias_primas:
            mp_por_proveedor[proveedor.id_proveedor].append({
                'id': mp.materia_prima.id_materiaPrima,
                'nombre': mp.materia_prima.nombre
            })
    return mp_por_proveedor

@compra_blueprint.route("/compras", methods=["GET", "POST"])
@login_required
def compraIndex():
    compras = Compra.query.all()
        
    return render_template("compra/compra.html", Compra=compras)

@compra_blueprint.route("/detalleCompra", methods=["GET", "POST"])
@login_required
def detalleCompraIndex():
    if request.method=='GET':
        id=request.args.get('id')
        dCompras = DetalleCompra.query.filter_by(compra_id_compra=id).all()
        
    return render_template("compra/detalleCompra.html", dCompra=dCompras)

@compra_blueprint.route("/compraForm", methods=["GET", "POST"])
@login_required
def compraForm():
    crpForm=forms.CompraForm(request.form)
    global MPrima
    global MPrimaTexto
    tCompra=0
    mapr = MateriasPrimas.query.filter_by(estatus=1).all()
    mpinfo = {materia.id_materiaPrima: materia.tipo_medida.descripcion for materia in mapr}

    tm = TipoMedidasMaterialPrimas.query.all()
    tminfo = {tipo.descripcion: tipo.id_medida for tipo in tm}
    pdm = obtener_mp_por_proveedor()
    if request.method=="POST":

        if request.form['buttonMP'] == "btnAgregarMP":
            cantidad=crpForm.cantidad.data
            tipoMP_id = tminfo.get(crpForm.TipoMedida.data, '')
            tipoMP_valor = crpForm.TipoMedida.data
            materiaprima_id = crpForm.idMateriaPrima.data
            materiaprima_valor = dict(crpForm.idMateriaPrima.choices).get(materiaprima_id)
            prvd_id = crpForm.idProveedor.data
            prvd_valor = dict(crpForm.idProveedor.choices).get(prvd_id)
            totalCompra = crpForm.totalCompra.data
            fechaCaducidad = crpForm.fechaCaducidad.data
            MPrima.append({ 
                           'cantidad': cantidad, 
                           'tipoMP':tipoMP_id, 
                           'materiaprima': materiaprima_id, 
                           'prvd':prvd_id,
                           'total':totalCompra,
                           'fechaCaducidad':fechaCaducidad
                           }
            )
            MPrimaTexto.append({ 
                           'cantidad': cantidad, 
                           'tipoMP':tipoMP_valor, 
                           'materiaprima': materiaprima_valor, 
                           'prvd':prvd_valor,
                           'total':totalCompra,
                           'fechaCaducidad':fechaCaducidad
                           }
            )
            tCompra = sum(item['total'] for item in MPrima)

        if request.form['buttonMP'] == "btnQuitarMP":
            indexEliminar = request.form.getlist('eliminar[]')
            indexEliminar = [int(index) for index in indexEliminar]
            MPrima = [materiap for i, materiap in enumerate(MPrima, 1) if i not in indexEliminar]
            MPrimaTexto = [materiav for i, materiav in enumerate(MPrimaTexto, 1) if i not in indexEliminar]
            tCompra = sum(item['total'] for item in MPrima)

        if request.form['buttonMP'] == "btnLimpiarMP":
            MPrima.clear()
            MPrimaTexto.clear()
            tCompra = sum(item['total'] for item in MPrima)

        #Alerta para Registrar        
        if request.form['buttonMP'] == "btnRegistrarMP":
            tCompra = sum(item['total'] for item in MPrima)
            if not MPrima:
                flash('Ingrese materias primas.', 'warning')
            else:
                cajaA=db.session.query(Caja).filter(Caja.id_caja==1).first()
                if cajaA.dineroTotal < (sum(item['total'] for item in MPrima)):
                    flash('No hay suficiente dinero en caja.', 'warning')
                else:
                    #tabla compra
                    uid = current_user.id_usuario
                    prvd=Compra(totalCompra=(sum(item['total'] for item in MPrima)), fecha_actualiza = datetime.now(), usuario_id_usuario = uid)
                    
                    db.session.add(prvd)
                    db.session.commit()
                    idCompra = db.session.query(db.func.max(Compra.id_compra)).scalar()

                    #tabla caja_retiro
                    detalle = CajaRetiro(descripcion=crpForm.descripcion.data, dineroSacado=(sum(item['total'] for item in MPrima)), caja_id_caja=1, compra_id_compra=idCompra)
                    db.session.add(detalle)
                    db.session.commit()

                    #restar de caja
                    cajaA.dineroTotal = (cajaA.dineroTotal - (sum(item['total'] for item in MPrima)))
                    #print(cajaA.dineroTotal - int(crpForm.totalCompra.data))
                    db.session.add(cajaA)
                    db.session.commit()
                    
                    #tabla detalle compra
                    for elemento in MPrima:
                        cantidad = elemento['cantidad']
                        tipoMP_id = elemento['tipoMP']
                        materiaprima_id = elemento['materiaprima']
                        prvd_id = elemento['prvd']
                        fechaCaducidad = elemento['fechaCaducidad']
                        precio = elemento['total']
                
                        detalle = DetalleCompra(cantidad=cantidad, tipomedidasmaterialprimas_id_medida=tipoMP_id, precio=precio,
                                                compra_id_compra=idCompra, materiasprimas_id_materiaPrima=materiaprima_id, 
                                                proveedor_id_proveedor=prvd_id)
                        db.session.add(detalle)
                        db.session.commit()

                        #registro detalle materia prima
                        detalleMP = DetalleMateriaPrima(cantidad=cantidad, caducidad=fechaCaducidad, precio=precio,
                                                mermado=0, materia_prima_id=materiaprima_id, 
                                                tipo_medida_id=tipoMP_id)
                        db.session.add(detalleMP)
                        db.session.commit()

                        #suma a materia prima
                        isrtMP=db.session.query(MateriasPrimas).filter(MateriasPrimas.id_materiaPrima==materiaprima_id).first()
                        isrtMP.cantidad = (isrtMP.cantidad + int(cantidad))
                        db.session.add(isrtMP)
                        db.session.commit()
                        
                    MPrima.clear()
                    MPrimaTexto.clear()
                    flash('Compra registrada.', 'warning')
                    return redirect(url_for('compras.compraIndex'))

        if request.form['buttonMP'] == "btnRegresarMP":
            MPrima.clear()
            MPrimaTexto.clear()
            return redirect(url_for('compras.compraIndex'))
            
    return render_template("compra/compraForm.html", crpForm=crpForm, MPrima=MPrimaTexto, mpinfo=mpinfo, pdm=pdm, tCompra=tCompra)