from flask import Blueprint, render_template, request
import blueprints.forms as forms
from blueprints.models import Galleta

venta_blueprint = Blueprint("ventas", __name__, template_folder="templates")
quedan_galletas = {
    "Chispas de Chocolate": 15,  
    "Mantequilla": 10,              
    "Avena": 9,                 
    "Macarrones" :6,
    "Jengibre":15,
    "Polvorones":25,
    "Pastisetas":25,
    "Nuez":20,
    "Coco":7,
    "Almendras":7,
}
menu_items = []
@venta_blueprint.route("/ventas", methods=["GET", "POST"])
def ventas():
    galletas=Galleta.query.all()
    galletasc = Galleta.query.filter(Galleta.cantidad < 10).all()
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
                
        return render_template('ventas/ventas.html', galletas=galletas, menu_items=menu_items,galletasc=galletasc)
    
    return render_template('ventas/ventas.html', galletas=galletas,galletasc=galletasc)