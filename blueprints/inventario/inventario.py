from flask import Blueprint, render_template, request
import blueprints.forms as forms
from blueprints.models import Galleta, MateriasPrimas

inventario_blueprint = Blueprint("inventario", __name__, template_folder="templates")

@inventario_blueprint.route("/inventario", methods=["GET", "POST"])
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
    return render_template("inventarios/inventario.html", galletas=galletas, materiasPrimas=materiasPrimas)