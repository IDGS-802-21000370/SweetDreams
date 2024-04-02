from flask import Blueprint, current_app, render_template, redirect, request
from blueprints.produccion.produccionGalletas import Guardar
from flask_sqlalchemy import SQLAlchemy

produccion_blueprint = Blueprint("produccion", __name__, template_folder="templates")

@produccion_blueprint.route("/produccionGalleta", methods=["GET", "POST"])
def produccionGalletas():
    galletas_en_preparacion = []
    galletas_preparadas = []

    if request.method == "POST":
        galleta_seleccionada = request.form["galleta"]
        Guardar.galletasenpreparacion(galleta_seleccionada)
        #Guardar.mandarmostrador()
    with open("blueprints/produccion/galletas_en_preparacion.txt", "r") as file:
        galletas_en_preparacion = file.readlines()
    
    with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
        galletas_preparadas = file.readlines()
          
    return render_template("produccion/produccionGalleta.html", galletas_en_preparacion=galletas_en_preparacion, galletas_preparadas=galletas_preparadas)


@produccion_blueprint.route("/enviarMostrador", methods=["POST"])
def enviarMostrador():
    Guardar.mandar_mostrador(current_app)
   
    return  render_template("produccion/produccionGalleta.html")