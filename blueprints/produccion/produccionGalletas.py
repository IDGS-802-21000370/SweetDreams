import threading
from cgitb import text
from datetime import datetime
import os
from flask import Flask, render_template,request,Response
import blueprints.forms as forms
from sqlalchemy import cast
from flask_wtf.csrf import CSRFProtect
from flask import g
from flask import flash
from blueprints.config import DevelopmentConfig
from flask_sqlalchemy import SQLAlchemy
from blueprints.models import DetalleGalleta, DetalleMateriaPrima, Galleta, Receta,DetalleReceta, MateriasPrimas, db


class Guardar:
    tiempos_galletas = {
        "Chispas de Chocolate": 10,  
        "Mantequilla": 10,              
        "Avena": 9,                 
        "Macarrones" :100,
        "Jengibre":15,
        "Polvorones":1,
        "Pastisetas":1,
        "Nuez":1,
        "Coco":1,
        "Almendras":1,
    }

    @staticmethod
    def galletasenpreparacion(galleta):
        # Agregar la galleta al archivo de galletas en preparación
        Guardar.escribir_galleta_en_preparacion(galleta)
        with open("blueprints/produccion/galletas_en_preparacion.txt", "a") as file:
            print("chi")
        # Iniciar un hilo para mover la galleta a las galletas preparadas después del tiempo especificado
        tiempo = Guardar.tiempos_galletas.get(galleta, 10)
        t = threading.Timer(tiempo, Guardar.galletaspreparadas, args=[galleta])
        t.start()
         
    @staticmethod
    def escribir_galleta_en_preparacion(galleta):
        try:
            with open("blueprints/produccion/galletas_en_preparacion.txt", "a") as file:
                file.write(f"{galleta}\n")
            print(f"Galleta {galleta} agregada a la lista de preparación.")
        except Exception as e:
            print(f"Error al agregar la galleta {galleta} a la lista de preparación: {e}")

    @staticmethod
    def galletaspreparadas(galleta):
        try:
            # Mover la galleta al archivo de galletas preparadas
            with open("blueprints/produccion/galletas_en_preparacion.txt", "r") as file:
                lines = file.readlines()
            with open("blueprints/produccion/galletas_en_preparacion.txt", "w") as file:
                for line in lines:
                    if line.strip() != galleta:
                        file.write(line)

            with open("blueprints/produccion/galletas_preparadas.txt", "a") as file:
                file.write(f"{galleta}\n")
              
            print(f"Galleta {galleta} preparada y agregada a la lista de galletas preparadas.")
            with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
                 file.readlines()
       
            # Recargar la página después de que se complete el tiempo
          
        except Exception as e:
            print(f"Error al agregar la galleta {galleta} a la lista de galletas preparadas: {e}")
    
    
  

    @staticmethod
    def mandar_mostrador(app):
        try:
            with app.app_context():
                # Leer el archivo de galletas preparadas y buscar en la base de datos las recetas correspondientes
                with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
                    galletas_preparadas = file.readlines()
                    for galleta_line in galletas_preparadas:
                        galleta_nombre = galleta_line.strip()  # Eliminar espacios en blanco y saltos de línea
                        receta = Receta.query.filter_by(nombre=galleta_nombre).first()
                        if receta:
                            # Actualizar la cantidad de galletas en función del total de galletas de la receta
                            galleta = Galleta.query.filter_by(nombre=galleta_nombre).first()
                            if galleta:
                                galleta.cantidad += receta.totalGalletas
                            else:
                                galleta = Galleta(nombre=galleta_nombre, cantidad=receta.totalGalletas)
                                db.session.add(galleta)
                            db.session.commit()
                                # Insertar un nuevo registro en DetalleGalleta
                            detalle_galleta = DetalleGalleta(cantidad=receta.totalGalletas, caducidad=datetime.now(), galleta_id_galleta=galleta.id_galleta)
                            db.session.add(detalle_galleta)
                            db.session.commit()
                            # Buscar los detalles de receta correspondientes a la receta encontrada
                            detalles_receta = DetalleReceta.query.filter_by(receta_id_receta=receta.id_receta).all()
                            for detalle in detalles_receta:
                                # Obtener la materia prima y actualizar su cantidad en DetalleReceta
                                materia_prima = db.session.get(MateriasPrimas, detalle.materiasprimas_id_materiaPrima)
                                if materia_prima:
                                    # Restar la cantidad utilizada en la receta
                                    materia_prima.cantidad -= detalle.cantidad
                                    db.session.commit()
                                    
                                # Descuentos también en la tabla DetalleMateriaPrima con mermado=0
                                materia_prima_id = detalle.materiasprimas_id_materiaPrima
                                detalle_materia_prima = DetalleMateriaPrima.query.filter_by(materia_prima_id=materia_prima_id, mermado=0).order_by(DetalleMateriaPrima.caducidad.asc()).first()
                                cantidad_requerida = detalle.cantidad
                                while detalle_materia_prima and cantidad_requerida > 0:
                                    if detalle_materia_prima.cantidad >= cantidad_requerida:
                                        # Si hay suficiente cantidad, restar y actualizar en DetalleMateriaPrima
                                        detalle_materia_prima.cantidad -= cantidad_requerida
                                        db.session.commit()
                                        cantidad_requerida = 0  # No queda cantidad por restar
                                    else:
                                        # Si no es suficiente, restar la cantidad disponible y eliminar el registro
                                        cantidad_requerida -= detalle_materia_prima.cantidad
                                        db.session.delete(detalle_materia_prima)
                                        db.session.commit()
                                        # Pasar al siguiente registro según la fecha de caducidad y mermado=0
                                        detalle_materia_prima = DetalleMateriaPrima.query.filter_by(materia_prima_id=materia_prima_id, mermado=0).filter(DetalleMateriaPrima.caducidad > detalle_materia_prima.caducidad).order_by(DetalleMateriaPrima.caducidad.asc()).first()
                    
                with open("blueprints/produccion/galletas_preparadas.txt", "w") as file:
                    file.truncate(0)
                print("Galletas enviadas al mostrador correctamente.")
        except Exception as e:
            print(f"Error al enviar galletas al mostrador: {e}")



