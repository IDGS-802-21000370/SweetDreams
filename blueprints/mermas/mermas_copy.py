import threading
from cgitb import text

import os
from flask import Flask, render_template,request,Response
import blueprints.forms as forms
from sqlalchemy import cast
from flask_wtf.csrf import CSRFProtect
from flask import g
from flask import flash

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from  blueprints.models import DetalleGalleta, DetalleMateriaPrima, Galleta, Receta,DetalleReceta, MateriasPrimas, db
from blueprints.config import DevelopmentConfig


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
from  blueprints.models import MateriasPrimas, Merma

from datetime import datetime,  timedelta
from sqlalchemy import and_
#mandar a merma producto por caducidad
class merma:
    def mandarmermaproductocaducidad():
        try:
            with app.app_context():
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
                    
                db.session.commit()
                print("Productos enviados a merma correctamente.")
        except Exception as e:
            print(f"Error al manejar las materias primas: {e}")

    #mandar a merma galleta por caducidad
    def mandarmermagalletacaducidad():
        try:
            with app.app_context():
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
                print("Galletas enviadas a merma correctamente.")
        except Exception as e:
            print(f"Error al manejar las galletas: {e}")
        

    def verificar_galletas_por_caducidad():
        try:
            with app.app_context():
                detalles_galleta = DetalleGalleta.query.filter(DetalleGalleta.mermado == 0).all()
                
                for detalle in detalles_galleta:
                    galleta = Galleta.query.get(detalle.galleta_id_galleta)
                    nombre_galleta = galleta.nombre if galleta else None
                    dias_transcurridos = (datetime.now() - detalle.caducidad).days
                    if dias_transcurridos >= 5:  
                        mensaje = f"Las galletas de tipo {nombre_galleta} han pasado 5 días desde que se produjeron. ¿Desea mandar merma? (si/no): "
                        respuesta = input(mensaje).lower().strip()
                        if respuesta == 'si':
                            merma.mandar_merma(detalle)
                    
        except Exception as e:
            print(f"Error al manejar las galletas: {e}")

    def mandar_merma(detalle):
        try:
            with app.app_context():
                # Obtener la galleta asociada al detalle
                galleta = Galleta.query.get(detalle.galleta_id_galleta)
                if galleta:
                    # Actualizar la cantidad de galletas
                    galleta.cantidad -= detalle.cantidad
                # Marcar el detalle como mermado
                detalle.mermado = 1
                # Calcular la fecha de merma
                fecha_merma = detalle.caducidad + timedelta(days=5)
                # Crear un registro de merma
                merma = Merma(
                    nombre="Merma por caducidad: {}".format(galleta.nombre if galleta else "Sin nombre"),
                    cantidad=detalle.cantidad,
                    caducidad=fecha_merma,
                    tipomerma_id_tipoMerma=2,
                    id_detalle_galleta=detalle.id_detalle_galleta
                )
                # Guardar la merma en la base de datos
                db.session.add(merma)
                db.session.commit()
                print("Galletas enviadas a merma correctamente.")
        except Exception as e:
            print(f"Error al mandar la merma: {e}")



    #mandar a merma galleta con boton
    def mandarmermagalletaProduccion(galleta_id):
        try:
            with app.app_context():
                detalle = DetalleGalleta.query.filter_by(mermado=0, galleta_id_galleta=galleta_id).first()
                if detalle:
                    galleta = Galleta.query.get(galleta_id)
                    if galleta and detalle.cantidad > 0:
                        galleta.cantidad -= 1
                        if galleta.cantidad <= 0:
                            db.session.delete(galleta)
                        detalle.cantidad -= 1
                        if detalle.cantidad <= 0:
                            db.session.delete(detalle)
                        merma = Merma(
                            nombre="Merma por caducidad: {}".format(galleta.nombre) if galleta.nombre else "Merma por caducidad",  # Nombre opcional para la merma
                            cantidad=1,
                            tipomerma_id_tipoMerma=1, 
                            id_detalle_galleta=detalle.id_detalle_galleta,
                            caducidad=datetime.now()
                        )
                        db.session.add(merma)
                    
                db.session.commit()
                print("Galletas enviadas a merma correctamente.")
        except Exception as e:
            print(f"Error al manejar las galletas: {e}")

    csrf=CSRFProtect()
    if __name__ == "__main__":
        # Ejemplo de uso
        # Ejemplo de uso
        csrf.init_app(app)
        db.init_app(app)
        with app.app_context():
            db.create_all()
        # Llamar a la función de verificación en algún punto de tu programa
            verificar_galletas_por_caducidad()
