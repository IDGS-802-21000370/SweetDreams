from flask import Blueprint, redirect, render_template, request, url_for
from blueprints.models import Proveedor, db
from blueprints.provedores import proveedor
import blueprints.forms as forms

proveedor_blueprint = Blueprint("provedores", __name__, template_folder="templates")

@proveedor_blueprint.route("/proveedores", methods=["GET", "POST"])
def proveedorIndex():
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    
    if request.method == "POST":
        if 'buttonP' in request.form:
            #Alerta para eliminar
            proveedor.eliminarP()
            return redirect(url_for('provedores.proveedorIndex'))
        
    return render_template("proveedor/proveedor.html", Proveedor=proveedores)


@proveedor_blueprint.route("/proveedoresForm", methods=["GET", "POST"])
def prooveedorForm():
    prvdForm=forms.ProveedorForm(request.form)
    if request.method=="POST":
        if request.form['btnPrv'] == "btnRegistrarPrv":
            #Alerta para registrar
            proveedor.indexP()
            return redirect(url_for('provedores.proveedorIndex'))
            
    return render_template("proveedor/proveedorForm.html", formProveedor=prvdForm)

@proveedor_blueprint.route("/proveedoresUpdate", methods=["GET", "POST"])
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
        return redirect(url_for('provedores.proveedorIndex'))
    return render_template("proveedor/proveedorM.html", formProveedor=prvdForm)