from flask import Blueprint, render_template, request
import blueprints.forms as forms
from blueprints.models import Compra, DetalleCompra, db

compra_blueprint = Blueprint("compras", __name__, template_folder="templates")

MPrima = []
MPrimaTexto = []
@compra_blueprint.route("/compras", methods=["GET", "POST"])
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