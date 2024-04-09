from datetime import datetime, timedelta
from flask import Blueprint, current_app, render_template, request
from sqlalchemy import func
import blueprints.forms as forms
from blueprints.models import Galleta, MateriasPrimas, Merma
from blueprints.mermas.mermas_copy import merma

inventario_blueprint = Blueprint("inventario", __name__, template_folder="templates")

from blueprints.models import DetalleGalleta, DetalleMateriaPrima,db

@inventario_blueprint.route("/inventario", methods=["GET", "POST"])
def inventario():
    tipo_medida_map = {
        '1': 'Gramos',
        '2': 'Piezas',
        '3': 'Mililitros',
        '4': 'Costales'
    }
    
    detalles_galleta = DetalleGalleta.query.all()
    detalles_materia_prima = DetalleMateriaPrima.query.all()
    galleta = Galleta.query.all()
    materia_prima = MateriasPrimas.query.all()
    materia_prima_hacer = MateriasPrimas.query.filter(MateriasPrimas.cantidad <= 100).all()
    productos_a_caducar = []
    productos_a_caducarg = []
    
    for detalle in detalles_galleta:
                          if detalle.mermado == 0 and detalle.caducidad + timedelta(days=5) <= datetime.now():
                               productos_a_caducar.append(detalle)

    for detalle in detalles_materia_prima:
        if detalle.mermado == 0 and detalle.caducidad - timedelta(days=5) <= datetime.now():
            productos_a_caducarg.append(detalle)

    if request.method == "POST":
        
        if request.form.get("accion") == "mermagalletacasi":
            detalle_id = request.form.get("detalle_id")  # Cambia el nombre del campo si es necesario
            if detalle_id:
                try:
                    with current_app.app_context():
                        detalle = DetalleGalleta.query.get(detalle_id)  # Obtener el detalle de la galleta por su ID
                        if detalle:
                            galletas = Galleta.query.get(detalle.galleta_id_galleta)  # Obtener la galleta asociada al detalle
                            if galletas:
                                # Actualizar la cantidad de galletas
                                galletas.cantidad -= detalle.cantidad
                            # Marcar el detalle como mermado
                            detalle.mermado = 1
                            # Calcular la fecha de merma
                            fecha_merma = detalle.caducidad + timedelta(days=5)
                            # Crear un registro de merma
                            merma = Merma(
                                nombre="Merma por caducidad: {}".format(galletas.nombre if galletas else "Sin nombre"),
                                cantidad=detalle.cantidad,
                                caducidad=fecha_merma,
                                tipomerma_id_tipoMerma=2,
                                id_detalle_galleta=detalle.id_detalle_galleta
                            )
                            # Guardar la merma en la base de datos
                            db.session.add(merma)
                            db.session.commit()
                            print("Galleta enviada a merma correctamente.")
                        
                        else:
                            print("No se encontró el detalle de la galleta correspondiente.")
                except Exception as e:
                    print(f"Error al mandar la merma: {e}")
            else:
                print("No se proporcionó un ID de detalle de galleta en la solicitud.")
        elif request.form.get("accion") == "descuentar_galleta":
            galleta_id = request.form.get("galleta_id")  # Cambia el nombre del campo si es necesario
            if galleta_id:
                try:
                    with current_app.app_context():
                        # Buscar la galleta por su ID
                        galletass = Galleta.query.get(galleta_id)
                        if galletass:
                            # Buscar el detalle de galleta más próximo a caducar y que no esté mermado
                            detalle = DetalleGalleta.query.filter_by(galleta_id_galleta=galleta_id, mermado=0)\
                              .order_by(DetalleGalleta.caducidad.asc())\
                              .first()
  
                              

                            #print(detalle)  
                            if detalle:
                                # Actualizar la cantidad de galletas
                                galletass.cantidad -= 1
                                # Actualizar el detalle de galleta
                                detalle.cantidad -= 1
                                if detalle.cantidad == 0:
                                 detalle.mermado = 1
                                merma = Merma(
                                    nombre="Merma por descuento de galleta: {}".format(galletass.nombre),
                                    cantidad=1,
                                    caducidad=detalle.caducidad,
                                    tipomerma_id_tipoMerma=1,  # Tipo de merma para descuento de galleta
                                    id_detalle_galleta=detalle.id_detalle_galleta
                                )
                                # Guardar la merma en la base de datos
                                db.session.add(merma)
                                db.session.commit()
                                print("Galleta y detalle de galleta descontados correctamente.")
                            else:
                                print("No se encontró un detalle de galleta disponible para descontar.")
                        else:
                            print("No se encontró la galleta correspondiente.")
                except Exception as e:
                    print(f"Error al descontar la galleta: {e}")
            else:
                print("No se proporcionó un ID de galleta en la solicitud.")
        diccionario_productos = {
        1: 100,  # ID del producto: cantidad a descontar
        2: 1,
        3: 2,
        # Agrega más productos según sea necesario
    }
        if request.form.get("accion") == "descuentar_producto":
            id_materiaPrima = request.form.get("id_materiaPrima")  # Obtén el ID del producto desde el formulario
            if id_materiaPrima:
                try:
                    with current_app.app_context():
                        cantidad_a_descontar = diccionario_productos.get(int(id_materiaPrima), 0)
                        print("Cantidad a descontar:", cantidad_a_descontar)
                        if cantidad_a_descontar <= 0:
                            print("Cantidad a descontar inválida para el producto.")

                        productoss = MateriasPrimas.query.get(id_materiaPrima)
                        
                        if productoss:
                            detalles_disponibles = DetalleMateriaPrima.query.filter_by(
                               id_detalle_materiaprima=productoss.id_materiaPrima,
                                mermado=0
                            ).order_by(DetalleMateriaPrima.caducidad.asc()).all()

                            cantidad_restante = cantidad_a_descontar

                            for detalle in detalles_disponibles:
                                if detalle.cantidad >= cantidad_restante:
                                    detalle.cantidad -= cantidad_restante
                                    cantidad_restante = 0
                                    if detalle.cantidad == 0:
                                        detalle.mermado = 1
                                    break
                                else:
                                    cantidad_restante -= detalle.cantidad
                                    detalle.mermado = 1
                            productoss.cantidad -=cantidad_a_descontar
                            if cantidad_restante > 0:
                                print("No hay suficiente cantidad disponible en los detalles de materia prima.")
                            else:
                                merma = Merma(
                                    nombre="Merma por descuento de materia prima: {}".format(productoss.nombre),
                                    cantidad=cantidad_a_descontar,
                                    caducidad=detalle.caducidad,
                                    tipomerma_id_tipoMerma=1,  # Tipo de merma para descuento de materia prima
                                    detallemateriaprima_id_detalle_materiaprima=detalle.id_detalle_materiaprima
                                )
                                db.session.add(merma)
                                db.session.commit()
                                print("Producto y detalle de producto descontados correctamente.")
                        else:
                            print("No se encontró la materia prima correspondiente.")
                except Exception as e:
                    print(f"Error al descontar el producto: {e}")
            else:
                print("No se proporcionó el ID del producto en la solicitud.")

    return render_template("inventarios/inventario.html", galleta=galleta, materia_prima=materia_prima, productos_a_caducar=productos_a_caducar, productos_a_caducarg=productos_a_caducarg, materia_prima_hacer= materia_prima_hacer)
