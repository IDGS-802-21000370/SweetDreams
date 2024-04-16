from flask import Blueprint, render_template, request, redirect, url_for
import blueprints.forms as forms
from blueprints.models import Compra, DetalleCompra, Caja, CajaRetiro, DetalleMateriaPrima, MateriasPrimas, db
from datetime import datetime
from flask_login import current_user, login_required
from functools import wraps

compra_blueprint = Blueprint("compras", __name__, template_folder="templates")
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            # Redirigir a una página de acceso denegado o a la página principal
            return render_template('404/404.html')
        return func(*args, **kwargs)
    return decorated_view

MPrima = []
MPrimaTexto = []
@compra_blueprint.route("/compras", methods=["GET", "POST"])
@admin_required
def compraIndex():
    compras = Compra.query.all()
        
    return render_template("compra/compra.html", Compra=compras)

@compra_blueprint.route("/detalleCompra", methods=["GET", "POST"])
def detalleCompraIndex():
    if request.method=='GET':
        id=request.args.get('id')
        dCompras = DetalleCompra.query.filter_by(compra_id_compra=id).all()
        
    return render_template("compra/detalleCompra.html", dCompra=dCompras)

@compra_blueprint.route("/compraForm", methods=["GET", "POST"])
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
            MPrimaTexto = [materiav for i, materiav in enumerate(MPrimaTexto, 1) if i not in indexEliminar]

        if request.form['buttonMP'] == "btnLimpiarMP":
            MPrima.clear()
            MPrimaTexto.clear()

        #Alerta para Registrar        
        if request.form['buttonMP'] == "btnRegistrarMP":

            if not MPrima:
                print("Ingrese materias primas a registrar")
            #Alert
            else:
                cajaA=db.session.query(Caja).filter(Caja.id_caja==1).first()
                if cajaA.dineroTotal < int(crpForm.totalCompra.data):
                    print("No hay suficiente dinero en caja")
                else:                    
                    #tabla compra
                    uid = current_user.id_usuario
                    prvd=Compra(totalCompra=crpForm.totalCompra.data, fecha_actualiza = datetime.now(), usuario_id_usuario = uid)
                    #prvd=Compra(totalCompra=crpForm.totalCompra.data, fecha_actualiza = datetime.now(), usuario_id_usuario = 1)
                    #Cambiar id_usuario por id del usuario loggeado
                    db.session.add(prvd)
                    db.session.commit()
                    idCompra = db.session.query(db.func.max(Compra.id_compra)).scalar()

                    #tabla caja_retiro
                    detalle = CajaRetiro(descripcion=crpForm.descripcion.data, dineroSacado=crpForm.totalCompra.data, caja_id_caja=1, compra_id_compra=idCompra)
                    db.session.add(detalle)
                    db.session.commit()

                    #restar de caja
                    cajaA.dineroTotal = (cajaA.dineroTotal - int(crpForm.totalCompra.data))
                    #print(cajaA.dineroTotal - int(crpForm.totalCompra.data))
                    db.session.add(cajaA)
                    db.session.commit()
                    
                    #tabla detalle compra
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

                        #registro detalle materia prima
                        detalleMP = DetalleMateriaPrima(cantidad=cantidad, caducidad=datetime.now(), 
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

    return render_template("compra/compraForm.html", formCompra=crpForm, MPrima=MPrimaTexto)