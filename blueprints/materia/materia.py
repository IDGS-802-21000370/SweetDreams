from flask import Blueprint, redirect, render_template, request, url_for
from blueprints.models import MateriasPrimas, DetalleProveedorMateria, db
from datetime import datetime
import blueprints.forms as forms

materiaprima_blueprint = Blueprint("materias", __name__, template_folder="templates")

@materiaprima_blueprint.route("/materiaprima", methods=["GET", "POST"])
def materiaprimaIndex():
    materias = MateriasPrimas.query.filter_by(estatus=1).all()
    
    if request.method == "POST":
        if 'buttonMP' in request.form:
            #Alerta para eliminar
            id = request.form['buttonMP']
            mtr=db.session.query(MateriasPrimas).filter(MateriasPrimas.id_materiaPrima==id).first()
            mtr.estatus = 0
            db.session.add(mtr)
            db.session.commit()

            detalle = DetalleProveedorMateria.query.filter_by(materiasprimas_id_materiaPrima=id).all()
            for detalle in detalle:
                detalle.estatus = 0
                db.session.commit()
            return redirect(url_for('materias.materiaprimaIndex'))
        
    return render_template("materia/materia.html", Materias=materias)

@materiaprima_blueprint.route("/materiaForm", methods=["GET", "POST"])
def materiaprimaForm():
    mtrForm = forms.MateriaForm(request.form)
    
    if request.method == "POST":
        if request.form['btnMtrP'] == "btnRegistrarMtrP":
            #Alerta para registrar
            formMtr=forms.MateriaForm(request.form)
            mtr=MateriasPrimas(nombre=formMtr.nombre.data, cantidad=0, caducidad=datetime.now(), tipomedidasmaterialprimas_id_medida = formMtr.tipoMedida.data)
            db.session.add(mtr)
            db.session.commit()
            return redirect(url_for('materias.materiaprimaIndex'))
        
    return render_template("materia/materiaForm.html", formMateria=mtrForm)

@materiaprima_blueprint.route("/materiaUpdate", methods=["GET", "POST"])
def materiaprimaUpdate():
    mtrForm = forms.gMateria(request.form)
    
    if request.method=='GET':
        id=request.args.get('id')
        prvdA=db.session.query(MateriasPrimas).filter(MateriasPrimas.id_materiaPrima==id).first()
        mtrForm.id.data=request.args.get('id')
        mtrForm.nombre.data=prvdA.nombre
        mtrForm.tipoMedida.data=prvdA.tipomedidasmaterialprimas_id_medida
    if request.method=="POST":
        #Alerta para editar
        id=mtrForm.id.data
        mtr=db.session.query(MateriasPrimas).filter(MateriasPrimas.id_materiaPrima==id).first()
        mtr.nombre=mtrForm.nombre.data
        mtr.tipomedidasmaterialprimas_id_medida=mtrForm.tipoMedida.data
        db.session.add(mtr)
        db.session.commit()
        return redirect(url_for('materias.materiaprimaIndex'))
        
    return render_template("materia/materiaUpdate.html", formMateria=mtrForm)

@materiaprima_blueprint.route("/materiaEliminada", methods=["GET", "POST"])
def materiaEliminado():
    mtrE = MateriasPrimas.query.filter_by(estatus=0).all()
    
    if request.method == "POST":
        if 'buttonMP' in request.form:
            #Alerta para restaurar
            id = request.form['buttonMP']
            mtr=db.session.query(MateriasPrimas).filter(MateriasPrimas.id_materiaPrima==id).first()
            mtr.estatus = 1
            db.session.add(mtr)
            db.session.commit()
            detalle = DetalleProveedorMateria.query.filter_by(materiasprimas_id_materiaPrima=id).all()
            for detalle in detalle:
                detalle.estatus = 1
                db.session.commit()
            return redirect(url_for('materias.materiaEliminado'))
        
    return render_template("materia/materiaEliminada.html", MateriasE=mtrE)