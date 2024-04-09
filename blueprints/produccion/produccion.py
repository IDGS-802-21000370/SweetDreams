from flask import Blueprint, current_app, jsonify, render_template, redirect, request
from blueprints.produccion.produccionGalletas import Guardar
from flask_sqlalchemy import SQLAlchemy

produccion_blueprint = Blueprint("produccion", __name__, template_folder="templates")

@produccion_blueprint.route("/produccionGalleta", methods=["GET", "POST"])
def produccionGalletas():
    galletas_en_preparacion = []
    galletas_preparadas = []
    galleta_enviada_al_mostrador = None
    galletas_preparadaditas=[]
    with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
        galletas_preparadaditas = [line.strip() for line in file.readlines()]
    ventana=False
    if request.method == "POST":
        if request.form.get("accion") == "Guardar":
            galleta_seleccionada = request.form["galleta"]
            Guardar.galletasenpreparacion(galleta_seleccionada)
            galleta_enviada_al_mostrador = galleta_seleccionada
            """ ventana=Guardar.ventana(galleta_seleccionada)
            print(ventana) """
            
            #Guardar.mandarmostrador()
        
        elif request.form.get("accion") == "Enviar al Mostrador":
            Guardar.mandar_mostrador(current_app)
        
        """  with open("blueprints/produccion/galletas_en_preparacion.txt", "r") as file:
                galletas_en_preparacion = file.readlines()
            
            with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
                galletas_preparadas = [line.strip() for line in file.readlines()] """
        if request.form.get("accion") == "Mostrar galletas Preparadas":
            with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
               galletas_preparadas = [line.strip() for line in file.readlines()]
        elif request.form.get("accion") == "Mostrar galletas en Preparacion":
             with open("blueprints/produccion/galletas_en_preparacion.txt", "r") as file:
              galletas_en_preparacion = file.readlines()
    return render_template("produccion/produccionGalleta.html", galletas_en_preparacion=galletas_en_preparacion, galletas_preparadas=galletas_preparadas,galleta_enviada_al_mostrador=galleta_enviada_al_mostrador,galletas_preparadaditas=galletas_preparadaditas)


""" @produccion_blueprint.route("/enviarMostrador", methods=["POST"])
def enviarMostrador():
    Guardar.mandar_mostrador(current_app)
   
    return  render_template("produccion/produccionGalleta.html") """
