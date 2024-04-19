from flask import Blueprint, redirect, render_template, request, url_for, flash
from blueprints.models import Proveedor, DetalleProveedorMateria, MateriasPrimas, db
from blueprints.provedores import provedor
import blueprints.forms as forms
from functools import wraps
from flask_login import current_user

proveedor_blueprint = Blueprint("provedores", __name__, template_folder="templates")
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            # Redirigir a una página de acceso denegado o a la página principal
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

MPrima = []
MPrimaTexto = []
DPrima = []
MPrimaM = []
MPrimaTextoM = []
@proveedor_blueprint.route("/proveedores", methods=["GET", "POST"])
@admin_required
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
            flash('Proveedor eliminado.', 'warning') 
            return redirect(url_for('provedores.proveedorIndex'))
        
    return render_template("proveedor/proveedor.html", Proveedor=proveedores)


@proveedor_blueprint.route("/proveedoresForm", methods=["GET", "POST"])
@admin_required
def prooveedorForm():
    prvdForm=forms.ProveedorForm(request.form)
    global MPrima
    global MPrimaTexto
    if request.method=="POST":

        if request.form['btnPrv'] == "btnAgregarPrv":
            materiaprima_id = prvdForm.materia.data
            materiaprima_valor = dict(prvdForm.materia.choices).get(materiaprima_id)
            MPrima.append({  
                           'materiaprima': materiaprima_id, 
                           }
            )
            MPrimaTexto.append({ 
                           'materiaprima': materiaprima_valor, 
                           }
            )
            
        if request.form['btnPrv'] == "btnQuitarPrv":
            indexEliminar = request.form.getlist('eliminar[]')
            indexEliminar = [int(index) for index in indexEliminar]
            MPrima = [materiap for i, materiap in enumerate(MPrima, 1) if i not in indexEliminar]
            MPrimaTexto = [materiav for i, materiav in enumerate(MPrimaTexto, 1) if i not in indexEliminar]
        
        materiaIds = [mp['materiaprima'] for mp in MPrima]
        materias_disponibles = MateriasPrimas.query.filter_by(estatus=1).filter(MateriasPrimas.id_materiaPrima.notin_(materiaIds)).all()
        prvdForm.materia.choices = [(mtr.id_materiaPrima, mtr.nombre) for mtr in materias_disponibles]
        
        if request.form['btnPrv'] == "btnRegistrarPrv":
            if not MPrimaM:
                flash('Ingrese materias primas al proveedor.', 'warning')
            else:
            #Alerta para registrar y checar que no haya datos repetidos en la tabla
                prvd_form=forms.ProveedorForm(request.form)
                nombreEmpresa=prvd_form.nombreEmpresa.data
                proveedorExistente = Proveedor.query.filter_by(nombreEmpresa=nombreEmpresa).first()
                if proveedorExistente:
                    flash('El nombre del proveedor  ya existe. Por favor, elija otro nombre.', 'warning') 
                else:
                    prvd=Proveedor(nombreEmpresa=prvd_form.nombreEmpresa.data, direccion = prvd_form.direccion.data, contacto = prvd_form.contacto.data)
                    db.session.add(prvd)
                    db.session.commit()

                    idPrv = db.session.query(db.func.max(Proveedor.id_proveedor)).scalar()
                    for elemento in MPrima:
                        materiaprima_id = elemento['materiaprima']
                            
                        detalle = DetalleProveedorMateria(materiasprimas_id_materiaPrima=materiaprima_id, proveedor_id_proveedor=idPrv)
                        db.session.add(detalle)
                        db.session.commit()
                                    
                    MPrima.clear()
                    MPrimaTexto.clear()
                    flash('Proveedor registrado.', 'warning')
                    return redirect(url_for('provedores.proveedorIndex'))

        if request.form['btnPrv'] == "btnRegresarPrv":
            MPrima.clear()
            MPrimaTexto.clear()
            return redirect(url_for('provedores.proveedorIndex'))
        
    return render_template("proveedor/proveedorForm.html", formProveedor=prvdForm, MPrima=MPrimaTexto)

@proveedor_blueprint.route("/proveedoresUpdate", methods=["GET", "POST"])
@admin_required
def prooveedorUpdate():
    global DPrima
    global MPrimaM
    global MPrimaTextoM
    prvdForm=forms.getProveedor(request.form)
    dmn = MateriasPrimas.query.filter_by(estatus=1).all()
    dmni = {materia.id_materiaPrima: materia.nombre for materia in dmn}
    if request.method=='GET':
        MPrimaM = []
        DPrima = []
        id=request.args.get('id')
        prvdA=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
        prvdForm.id.data=request.args.get('id')
        prvdForm.nombreEmpresa.data=prvdA.nombreEmpresa
        prvdForm.direccion.data=prvdA.direccion
        prvdForm.contacto.data=prvdA.contacto
        dpm = DetalleProveedorMateria.query.filter_by(proveedor_id_proveedor=id, estatus=1).all()

        for detalle in dpm:
            MPrimaM.append({
                'materiasprimas_id_materiaPrima': detalle.materiasprimas_id_materiaPrima,
                'materia_prima': dmni.get(detalle.materiasprimas_id_materiaPrima, '')
            })

            DPrima.append({
                'materiasprimas_id_materiaPrima': detalle.materiasprimas_id_materiaPrima,
                'proveedor_id_proveedor': detalle.proveedor_id_proveedor
            })
        materiaS = [mpm['materiasprimas_id_materiaPrima'] for mpm in MPrimaM]
        materias_disponibles = MateriasPrimas.query.filter_by(estatus=1).filter(MateriasPrimas.id_materiaPrima.notin_(materiaS)).all()
        prvdForm.materia.choices = [(mtr.id_materiaPrima, mtr.nombre) for mtr in materias_disponibles]
        
    if request.method=="POST":
        
        if request.form['btnPrvM'] == "btnAgregarPrv":
            materiaprima_id = prvdForm.materia.data
            id=prvdForm.id.data
            nombre = dmni.get(materiaprima_id, '')
            MPrimaM.append({  
                            'materiasprimas_id_materiaPrima': materiaprima_id,
                            'materia_prima': nombre
                           }
            )
            DPrima.append({ 
                            'materiasprimas_id_materiaPrima': materiaprima_id,
                            'proveedor_id_proveedor': id
                           }
            )

        if request.form['btnPrvM'] == "btnQuitarPrv":
            indice = request.form.getlist('quitar[]')
            indice = [int(index) for index in indice]
            MPrimaM = [materiap for i, materiap in enumerate(MPrimaM, 1) if i not in indice]
            DPrima = [materiap for i, materiap in enumerate(DPrima, 1) if i not in indice]
            
        materiaS = [mpm['materiasprimas_id_materiaPrima'] for mpm in MPrimaM]
        materias_disponibles = MateriasPrimas.query.filter_by(estatus=1).filter(MateriasPrimas.id_materiaPrima.notin_(materiaS)).all()
        prvdForm.materia.choices = [(mtr.id_materiaPrima, mtr.nombre) for mtr in materias_disponibles]

        if request.form['btnPrvM'] == "btnModificarrPrv":
            #Alerta para editar
            if not MPrimaM:
                flash('Ingrese materias primas o elimine proveedor.', 'warning')
            else:
                id=prvdForm.id.data
                prvd=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
                prvd.nombreEmpresa=prvdForm.nombreEmpresa.data
                prvd.direccion=prvdForm.direccion.data
                prvd.contacto=prvdForm.contacto.data
                db.session.add(prvd)
                db.session.commit()
                
                detalleproveedor = DetalleProveedorMateria.query.filter_by(proveedor_id_proveedor=id).all()
                # Actualizar los detalles existentes y agregar los nuevos
                for detalle in detalleproveedor:
                    mtrid = detalle.materiasprimas_id_materiaPrima
                    
                    # Si el detalle existe en la lista DPrima, establecer su estatus como 1
                    if any(mtrid == elemento['materiasprimas_id_materiaPrima'] for elemento in DPrima):
                        detalle.estatus = 1
                        db.session.commit()
                    else:
                        detalle.estatus = 0
                        db.session.commit()
                
                # Agregar nuevos detalles de materia prima que no están en los detalles del proveedor
                for elemento in DPrima:
                    mtrid = elemento['materiasprimas_id_materiaPrima']
                    if not any(mtrid == detalle.materiasprimas_id_materiaPrima for detalle in detalleproveedor):
                        detalle = DetalleProveedorMateria(materiasprimas_id_materiaPrima=mtrid, proveedor_id_proveedor=id)
                        db.session.add(detalle)
                        db.session.commit()
                flash('Proveedor actualizado.', 'warning') 
                return redirect(url_for('provedores.proveedorIndex'))
                
    return render_template("proveedor/proveedorM.html", formProveedor=prvdForm,MPrimaM=MPrimaM)

@proveedor_blueprint.route("/proveedorE", methods=["GET", "POST"])
@admin_required
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
            flash('Proveedor restaurado.', 'warning') 
            return redirect(url_for('provedores.proveedorEliminado'))
        
    return render_template("proveedor/proveedorE.html", Proveedor=proveedores)