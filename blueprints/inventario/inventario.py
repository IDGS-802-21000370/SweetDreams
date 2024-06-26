from datetime import datetime, timedelta
from flask import Blueprint, current_app, flash, render_template, request, redirect, url_for
from sqlalchemy import func
import blueprints.forms as forms
from blueprints.models import Galleta, MateriasPrimas, Merma
from blueprints.mermas.mermas_copy import merma
from functools import wraps
from flask_login import current_user

inventario_blueprint = Blueprint("inventario", __name__, template_folder="templates")

from blueprints.models import DetalleGalleta, DetalleMateriaPrima,db
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

@inventario_blueprint.route("/inventario", methods=["GET", "POST"])
@login_required
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
        1: 658, 
        2: 1,
        3: 2,

       
    }
        if request.form.get("accion") == "descuentar_producto":
            id_materiaPrima = request.form.get("id_materiaPrima") 

            if id_materiaPrima:
                try:
                    with current_app.app_context():
                       
                        #cantidad_a_descontar = diccionario_productos.get(int(id_materiaPrima), 0)
                        cantidad_a_descontar = 1
                        print("Cantidad a descontar:", cantidad_a_descontar)
                         
                        productoss = MateriasPrimas.query.get(id_materiaPrima)
                       
                        if productoss:
                            
                            detalle = DetalleMateriaPrima.query.filter_by(
                                materia_prima_id=id_materiaPrima, 
                                mermado=0
                            ).order_by(DetalleMateriaPrima.caducidad.asc()).first()
                            if detalle:
                              if productoss.cantidad < 1:
                                flash("no tienes suficientes materias primas ")
                              else:
                                    productoss.cantidad -= cantidad_a_descontar
                                
                                    detalle.cantidad -= cantidad_a_descontar
                                    if detalle.cantidad == 0:
                                        detalle.mermado = 1
                                        
                                    merma = Merma(
                                        nombre=f"Merma por descuento de materia prima: {productoss.nombre}",
                                        cantidad=cantidad_a_descontar,
                                        caducidad=detalle.caducidad,
                                        tipomerma_id_tipoMerma=1,  
                                        materiasprimas_id_materiaPrima=detalle.id_detalle_materiaprima
                                    )
                                
                                    db.session.add(merma)
                                    db.session.commit()
                                    flash("Producto y detalle de producto descontados correctamente.")
                        else:
                            print("No se encontró la materia prima correspondiente.")
                except Exception as e:
                    print(f"Error al descontar el producto: {e}")
            else:
                print("No se proporcionó el ID del producto en la solicitud.")
    return render_template("inventarios/inventario.html", galleta=galleta, materia_prima=materia_prima, productos_a_caducar=productos_a_caducar, productos_a_caducarg=productos_a_caducarg, materia_prima_hacer= materia_prima_hacer)
