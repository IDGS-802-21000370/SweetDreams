from flask import Blueprint, redirect, render_template, request, url_for
from blueprints.models import Proveedor, db
from blueprints.provedores import provedor
import blueprints.forms as forms
from functools import wraps
from flask_login import current_user

proveedor_blueprint = Blueprint("provedores", __name__, template_folder="templates")

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

@proveedor_blueprint.route("/proveedores", methods=["GET", "POST"])
@login_required
def proveedorIndex():
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    
    if request.method == "POST":
        if 'buttonP' in request.form:
            #Alerta para eliminar
            id = request.form['buttonP']
            prvd=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
            prvd.estatus = 0
            db.session.add(prvd)
            db.session.commit()
            return redirect(url_for('provedores.proveedorIndex'))
        
    return render_template("proveedor/proveedor.html", Proveedor=proveedores)


@proveedor_blueprint.route("/proveedoresForm", methods=["GET", "POST"])
@login_required
def prooveedorForm():
    prvdForm=forms.ProveedorForm(request.form)
    if request.method=="POST":
        if request.form['btnPrv'] == "btnRegistrarPrv":
            #Alerta para registrar
            prvd_form=forms.ProveedorForm(request.form)
            prvd=Proveedor(nombreEmpresa=prvd_form.nombreEmpresa.data, direccion = prvd_form.direccion.data, contacto = prvd_form.contacto.data)
            db.session.add(prvd)
            db.session.commit()
            return redirect(url_for('provedores.proveedorIndex'))
            
    return render_template("proveedor/proveedorForm.html", formProveedor=prvdForm)

@proveedor_blueprint.route("/proveedoresUpdate", methods=["GET", "POST"])
@login_required
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

@proveedor_blueprint.route("/proveedorE", methods=["GET", "POST"])
@login_required
def proveedorEliminado():
    proveedores = Proveedor.query.filter_by(estatus=0).all()
    
    if request.method == "POST":
        if 'buttonP' in request.form:
            #Alerta para restaurar
            id = request.form['buttonP']
            prvd=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
            prvd.estatus = 1
            db.session.add(prvd)
            db.session.commit()
            return redirect(url_for('provedores.proveedorEliminado'))
        
    return render_template("proveedor/proveedorE.html", Proveedor=proveedores)