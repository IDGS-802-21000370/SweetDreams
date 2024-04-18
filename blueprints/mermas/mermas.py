from datetime import datetime, timedelta  # Importa la clase timedelta para manejar fechas
from flask import Blueprint, current_app, render_template, request, redirect, url_for
from sqlalchemy import and_
from functools import wraps
from flask_login import current_user
from blueprints.models import DetalleMateriaPrima, MateriasPrimas, Merma, db, DetalleGalleta, Galleta

mermas_blueprint = Blueprint("mermas", __name__, template_folder="templates")

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

@mermas_blueprint.route("/mermas", methods=["GET", "POST"])
@login_required
def mermas():
    try:
        with current_app.app_context():
            # Manejo de materias primas
            detalles_materia_prima = DetalleMateriaPrima.query.filter(and_(DetalleMateriaPrima.mermado == 0, DetalleMateriaPrima.caducidad < datetime.now())).all()
            
            for detalle in detalles_materia_prima:
                materia_prima = MateriasPrimas.query.get(detalle.materia_prima_id)
                if materia_prima:
                    materia_prima.cantidad -= detalle.cantidad
                detalle.mermado = 1
                nombre_materia_prima = materia_prima.nombre if materia_prima else None
                merma = Merma(
                    nombre="Merma por caducidad : {}".format(nombre_materia_prima) if nombre_materia_prima else "Merma por caducidad",  # Nombre opcional para la merma
                    cantidad=detalle.cantidad,
                    caducidad=detalle.caducidad,
                    tipomerma_id_tipoMerma=2,  
                    materiasprimas_id_materiaPrima=detalle.materia_prima_id,
                    detallemateriaprima_id_detalle_materiaprima=detalle.id_detalle_materiaprima
                )
                db.session.add(merma)
                
            # Manejo de galletas
            detalles_galleta = DetalleGalleta.query.filter(DetalleGalleta.mermado == 0).all()
            
            for detalle in detalles_galleta:
                galleta = Galleta.query.get(detalle.galleta_id_galleta)
                nombre_galleta = galleta.nombre if galleta else None
                dias_transcurridos = (datetime.now() - detalle.caducidad).days
                dias_especificos = {
                    "Chispas de Chocolate": 10,  
                    "Mantequilla": 10,              
                    "Avena": 9,                 
                    "Macarrones" :6,
                    "Jengibre":15,
                    "Polvorones":10,
                    "Pastisetas":10,
                    "Nuez":9,
                    "Coco":7,
                    "Almendras":7,
                }
                if nombre_galleta in dias_especificos and dias_transcurridos >= dias_especificos[nombre_galleta]:
                    if galleta:
                        galleta.cantidad -= detalle.cantidad
                    detalle.mermado = 1
                    fecha_merma = detalle.caducidad + timedelta(days=dias_especificos[nombre_galleta])
                    merma = Merma(
                        nombre="Merma por caducidad: {}".format(nombre_galleta) if nombre_galleta else "Merma por caducidad",  # Nombre opcional para la merma
                        cantidad=detalle.cantidad,
                        caducidad=fecha_merma,
                        tipomerma_id_tipoMerma=2, 
                        id_detalle_galleta=detalle.id_detalle_galleta
                    )
                    db.session.add(merma)
                
            db.session.commit()
            print("Productos enviados a merma correctamente.")
    except Exception as e:
        print(f"Error al manejar las materias primas: {e}")
    mermas_tipo_1 = Merma.query.filter_by(tipomerma_id_tipoMerma=1).all()
    mermas_tipo_2 = Merma.query.filter_by(tipomerma_id_tipoMerma=2).all()
    return render_template("mermas/mermas.html",mermas_tipo_1=mermas_tipo_1, mermas_tipo_2=mermas_tipo_2)
