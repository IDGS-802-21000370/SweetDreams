import threading
from cgitb import text
from datetime import datetime
import os
import time
from flask import Flask, render_template,request,Response
from flask_socketio import SocketIO

import blueprints.forms as forms
from sqlalchemy import cast
from flask_wtf.csrf import CSRFProtect
from flask import g
from flask import flash
from blueprints.config import DevelopmentConfig
from flask_sqlalchemy import SQLAlchemy
from blueprints.models import DetalleGalleta, DetalleMateriaPrima, Galleta, Receta,DetalleReceta, MateriasPrimas, db


class Guardar:
    def galletasenpreparacion(galleta):
        Guardar.escribir_galleta_en_preparacion(galleta)
        receta = Receta.query.join(DetalleReceta).join(Galleta).filter(Galleta.nombre == galleta).first()
        if receta:
           
            tiempo = receta.tiempo
        else:
            tiempo = 10  
        t = threading.Timer(tiempo, Guardar.galletaspreparadas, args=[galleta])
        t.start()  
        flash("Galleta en proceso de preparacion", "warning")
       
    def escribir_galleta_en_preparacion(galleta):
        try:
            with open("blueprints/produccion/galletas_en_preparacion.txt", "a") as file:
                file.write(f"{galleta}\n")
            print(f"Galleta {galleta} agregada a la lista de preparación.")
        except Exception as e:
            print(f"Error al agregar la galleta {galleta} a la lista de preparación: {e}")

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
        
            """ # Recargar la página después de que se complete el tiempo
            tiempo = Guardar.tiempos_galletas.get(galleta, 10)
            t2 = threading.Timer(tiempo, Guardar.leer_galletas_preparadas)
            t2.start() """
            #SocketIO.emit('galleta_preparada', galleta)
        except Exception as e:
            print(f"Error al agregar la galleta {galleta} a la lista de galletas preparadas: {e}")
    
    def leer_galletas_preparadas():
        # Leer el archivo de galletas preparadas
        with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
            galletas_preparadas = file.readlines()
        print("Galletas preparadas:", galletas_preparadas)
   
    def mandar_mostrador(app):
        try:
            with app.app_context():
                with open("blueprints/produccion/galletas_preparadas.txt", "r") as file:
                    galletas_preparadas = file.readlines()
                    for galleta_line in galletas_preparadas:
                        galleta_nombre = galleta_line.strip()  
                        receta = Receta.query.filter_by(nombre=galleta_nombre).first()
                        if receta:
                            galleta = Galleta.query.filter_by(nombre=galleta_nombre).first()
                            if galleta:
                                galleta.cantidad += receta.totalGalletas
                            else:
                                galleta = Galleta(nombre=galleta_nombre, cantidad=receta.totalGalletas)
                                db.session.add(galleta)
                            db.session.commit()
                            detalle_galleta = DetalleGalleta(cantidad=receta.totalGalletas, caducidad=datetime.now(), galleta_id_galleta=galleta.id_galleta)
                            db.session.add(detalle_galleta)
                            db.session.commit()
                            detalles_receta = DetalleReceta.query.filter_by(receta_id_receta=receta.id_receta).all()
                            for detalle in detalles_receta:
                                materia_prima = db.session.get(MateriasPrimas, detalle.materiasprimas_id_materiaPrima)
                                if materia_prima:
                                    materia_prima.cantidad -= detalle.cantidad
                                    db.session.commit()
                                    
    
                                materia_prima_id = detalle.materiasprimas_id_materiaPrima
                                detalle_materia_prima = DetalleMateriaPrima.query.filter_by(materia_prima_id=materia_prima_id, mermado=0).order_by(DetalleMateriaPrima.caducidad.asc()).first()
                                cantidad_requerida = detalle.cantidad
                                while detalle_materia_prima and cantidad_requerida > 0:
                                    if detalle_materia_prima.cantidad >= cantidad_requerida:
                                        
                                        detalle_materia_prima.cantidad -= cantidad_requerida
                                        db.session.commit()
                                        cantidad_requerida = 0  
                                    else:
                                        
                                        cantidad_requerida -= detalle_materia_prima.cantidad
                                        db.session.delete(detalle_materia_prima)
                                        db.session.commit()
                                        
                                        detalle_materia_prima = DetalleMateriaPrima.query.filter_by(materia_prima_id=materia_prima_id, mermado=0).filter(DetalleMateriaPrima.caducidad > detalle_materia_prima.caducidad).order_by(DetalleMateriaPrima.caducidad.asc()).first()
                    
                with open("blueprints/produccion/galletas_preparadas.txt", "w") as file:
                    file.truncate(0)
                print("Galletas enviadas al mostrador correctamente.")
        except Exception as e:
            print(f"Error al enviar galletas al mostrador: {e}")


    def obtener_nombres_galletas():
        nombres_galletas = []
        try:
            
            nombres_galletas= Receta.query.all()  
        except Exception as e:
            print(f"Error al obtener nombres de galletas desde la base de datos: {e}")
        return nombres_galletas
