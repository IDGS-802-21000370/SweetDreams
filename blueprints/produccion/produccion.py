import os
from flask import Blueprint, current_app, flash, jsonify, render_template, redirect, request
from blueprints.models import DetalleGalleta, DetalleReceta, Galleta, MateriasPrimas, Receta
from blueprints.produccion.produccionGalletas import Guardar
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from functools import wraps

produccion_blueprint = Blueprint("produccion", __name__, template_folder="templates")
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

@produccion_blueprint.route("/produccionGalleta", methods=["GET", "POST"])
@login_required
def produccionGalletas():
    galletas_en_preparacion = []
    galletas_preparadas = []
    galleta_enviada_al_mostrador = None
    galletas_preparadaditas=[]
    nombres_galletas = Guardar.obtener_nombres_galletas()
    with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
        galletas_preparadaditas = [line.strip() for line in file.readlines()]
    ventana=False
    
    if request.method == "POST":
        if request.form.get("accion") == "Guardar":
            galleta_seleccionada = request.form["galleta"]
            detalles_receta = DetalleReceta.query.join(Receta).join(Galleta).filter(Galleta.nombre == galleta_seleccionada).all()
            disponibilidad_materia_prima = True
            for detalle in detalles_receta:
                materia_prima_id = detalle.materiasprimas_id_materiaPrima
                materia_prima = MateriasPrimas.query.get(materia_prima_id)
                if materia_prima is None or materia_prima.cantidad < detalle.cantidad:
                    disponibilidad_materia_prima = False
                    break 
            if disponibilidad_materia_prima:
                Guardar.galletasenpreparacion(galleta_seleccionada)
                galleta_enviada_al_mostrador = galleta_seleccionada
            else:
                 flash("No hay suficiente materia prima para producir la galleta.", "warning")

        
        elif request.form.get("accion") == "Enviar al Mostrador":
            ruta_archivo = "blueprints/produccion/galletas_preparadas.txt"

            if os.path.exists(ruta_archivo):
              with open(ruta_archivo, 'r') as archivo:
               contenido = archivo.read()
               if not contenido:
                flash("El archivo de galletas está vacío.", "warning")
               else:
                Guardar.mandar_mostrador(current_app)
            else:
              flash("El archivo de galletas no existe.", "warning")
             
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
    return render_template("produccion/produccionGalleta.html", galletas_en_preparacion=galletas_en_preparacion, galletas_preparadas=galletas_preparadas,galleta_enviada_al_mostrador=galleta_enviada_al_mostrador,galletas_preparadaditas=galletas_preparadaditas, nombres_galletas= nombres_galletas)


""" @produccion_blueprint.route("/enviarMostrador", methods=["POST"])
def enviarMostrador():
    Guardar.mandar_mostrador(current_app)
   
    return  render_template("produccion/produccionGalleta.html") """
