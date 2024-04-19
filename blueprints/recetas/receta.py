import base64
import datetime
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
import blueprints.forms as forms
from blueprints.models import DetalleReceta, MateriasPrimas, Receta, TipoMedidasMaterialPrimas, db
from functools import wraps
from blueprints.models import DetalleReceta, Galleta, MateriasPrimas, Receta, TipoMedidasMaterialPrimas, db
from  functools import wraps
from flask_login import current_user

recetas_blueprint = Blueprint("recetas", __name__, template_folder="templates")
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

contador_recetas = 0
@recetas_blueprint.route("/recetas", methods=["GET", "POST"])
@login_required
def recetas():
    formReceta=forms.RecetaForm(request.form)
    materiasPrimas=MateriasPrimas.query.all()
    cargarMateriasPrimas=[]
    tipo_medida_map = {
        '1': 'Gramos',
        '2': 'Piezas',
        '3': 'Mililitros',
        '4': 'Costales'
    }

    tipoMedidaMateriaPrima=TipoMedidasMaterialPrimas.query.all()
    if request.method=="POST":
        ingrediente = request.form['materiasPrimas']
        cantidad = request.form['cantidad']
        tipoMedida = request.form['tipoMedidaMateriaPrima']
        
        if 'registrar' in request.form:
            if cantidad == '':
                return render_template("recetas/recetas.html", formReceta = formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, modal_cantidad=True)
            else:    
                materiaPrima = MateriasPrimas.query.filter_by(id_materiaPrima=int(ingrediente)).all()
                with open("recetas.txt", "r",  encoding="utf-8") as file:
                    recetas = file.readlines()
                lista_diccionarios = []
                for cadena in recetas:
                    pares = cadena.strip().split(', ')
                    diccionario = {}
                    for par in pares:
                        clave, valor = par.split(': ')
                        diccionario[clave] = valor
                    lista_diccionarios.append(diccionario)
                for elegido in lista_diccionarios:
                    if materiaPrima[0].nombre == elegido['ingrediente']:
                        flash("El ingrediente ya esta en la receta")
                        return render_template("recetas/recetas.html", formReceta = formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima)
                    else:
                        print(f"Prosigue la receta")
                ingrediente = materiaPrima[0].nombre
                tipoMedida = tipo_medida_map.get(tipoMedida, '')
                global contador_recetas
                contador_recetas += 1
                with open("recetas.txt", "a", encoding="utf-8") as file:
                    file.write(f"id_catReceta: {contador_recetas}, ingrediente: {ingrediente}, cantidad: {cantidad}, tipoMedida: {tipoMedida}\n")
                
                with open("recetas.txt", "r",  encoding="utf-8") as file:
                        recetas = file.readlines()
                receta_formateada=[]
                for dato in recetas:
                    partes = dato.strip().split(", ")
                    receta = {}
                    for parte in partes:
                        if ": " in parte:
                            clave, valor = parte.split(": ", 1)
                            receta[clave] = valor
                    receta_formateada.append(receta)
                return render_template("recetas/recetas.html", formReceta = formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, receta=receta_formateada)
        elif 'eliminar' in request.form:
            id = int(request.form['eliminar'])
            with open("recetas.txt", "r", encoding="utf-8") as file:
                lineas = file.readlines()

            with open("recetas.txt", "w", encoding="utf-8") as file:
                for linea in lineas:
                    partes = linea.strip().split(", ")
                    for parte in partes:
                        if "id_catReceta: " in parte:
                            receta_id = int(parte.split(": ")[1])
                            if receta_id == id:
                                break
                    else:
                        file.write(linea)
            with open("recetas.txt", "r",  encoding="utf-8") as file:
                recetas = file.readlines()
            if len(recetas) != 0:
                receta_formateada = []
                for dato in recetas:
                    partes = dato.strip().split(", ")
                    receta = {}
                    for parte in partes:
                        if ": " in parte:
                            clave, valor = parte.split(": ", 1)
                            receta[clave] = valor
                    receta_formateada.append(receta)
                return render_template("recetas/recetas.html", formReceta = formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, receta=receta_formateada)
        elif 'insertar' in request.form:
            formReceta = forms.RecetaForm(request.form)
            try:
                with open('recetas.txt', 'r') as archivo:
                    # Realiza operaciones con el archivo
                    contenido = archivo.read()
                    print(contenido)
            except FileNotFoundError:
                return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal_campos_ingrdientes=True)

            if formReceta.nombreReceta.data == '' or formReceta.descripcion.data == '' or formReceta.totalGalletas == '' or formReceta.tiempoHornear == '' or formReceta.precioTotal == '' or request.form['pesajeGramos'] == '':
                return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal_campos=True)
            else: 
                if request.form['id_receta'] != '' and request.form['id_receta'] != 'None':
                    return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal=True, id_re=request.form['id_receta'])
                else:
                    archivo = request.files['file']
                    ruta_archivo = archivo.filename

                    receta = Receta(nombre=formReceta.nombreReceta.data,
                                descripcion=formReceta.descripcion.data,
                                totalGalletas=int(formReceta.totalGalletas.data),
                                tiempoHornear=int(formReceta.tiempoHornear.data),
                                precioTotal=int(formReceta.precioTotal.data),
                                fecha_actualiza=datetime.datetime.now())
                    db.session.add(receta)
                    db.session.commit()
                    
                    ultimaReceta = Receta.query.order_by(Receta.id_receta.desc()).limit(1).first()
                    pesajeGramos =  request.form['pesajeGramos']
                    precioXgalleta = float(formReceta.precioTotal.data) // float(formReceta.totalGalletas.data)
                    precioPiezaGalleta = precioXgalleta * 1.03
                    precioPaquete1 = round(700 // float(pesajeGramos)) * 1.03
                    precioPaquete2 = round(1000 // float(pesajeGramos)) * 1.03
                    insertarGalleta = Galleta(nombre = formReceta.nombreReceta.data,
                                            cantidad = 0,
                                            precio = precioXgalleta,
                                            caducidad = datetime.datetime.now(),
                                            pesajeGramos = float(pesajeGramos),
                                            precioPieza = precioPiezaGalleta,
                                            precioGramos = 0,
                                            precioPaquete1 = precioPaquete1,
                                            precioPaquete2 = precioPaquete2,
                                            imagen = ruta_archivo,
                                            receta_id_receta = ultimaReceta.id_receta
                                            )
                    db.session.add(insertarGalleta)
                    db.session.commit()
                    
                    with open("recetas.txt", "r",  encoding="utf-8") as file:
                        recetas = file.readlines()
                    if len(recetas) != 0:
                        receta_formateada = []
                        for dato in recetas:
                            partes = dato.strip().split(", ")
                            receta = {}
                            for parte in partes:
                                if ": " in parte:
                                    clave, valor = parte.split(": ", 1)
                                    receta[clave] = valor
                            receta_formateada.append(receta)
                    receta = Receta.query.order_by(Receta.id_receta.desc()).limit(1).first()
                    for r in range(len(receta_formateada)):
                        materiasPrimas = MateriasPrimas.query.filter_by(nombre=receta_formateada[r]['ingrediente']).all()
                        id_materiaPrima = materiasPrimas[0].id_materiaPrima
                        tipoMedida = TipoMedidasMaterialPrimas.query.filter_by(descripcion=receta_formateada[r]['tipoMedida']).all()
                        id_tipoMedida = tipoMedida[0].id_medida

                        detalleReceta = DetalleReceta(cantidad=receta_formateada[r]['cantidad'],
                                                    receta_id_receta=receta.id_receta,
                                                    materiasprimas_id_materiaPrima=id_materiaPrima,
                                                    tipomedidasmaterialprimas_id_medida=id_tipoMedida)
                        db.session.add(detalleReceta)
                        db.session.commit()
                    os.remove("recetas.txt")
                    return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal=False)
        elif 'cargar' in request.form:
                recetasCargadas=Receta.query.all()
                return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, recetasCargadas=recetasCargadas)
        elif 'obtenerModificar' in request.form:
            formReceta=forms.RecetaForm(request.form)
            cargarReceta = Receta.query.filter_by(id_receta=int(request.form['obtenerModificar'])).all()
            formReceta.id_receta.data = cargarReceta[0].id_receta
            formReceta.nombreReceta.data = cargarReceta[0].nombre
            formReceta.descripcion.data = cargarReceta[0].descripcion
            formReceta.totalGalletas.data = str(cargarReceta[0].totalGalletas)
            formReceta.tiempoHornear.data = str(cargarReceta[0].tiempoHornear)
            formReceta.precioTotal.data = str(cargarReceta[0].precioTotal)
            return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, cargarReceta=cargarReceta)
        elif 'actualizar' in request.form:
            formReceta=forms.RecetaForm(request.form)
            try:
                with open('recetas.txt', 'r') as archivo:
                    # Realiza operaciones con el archivo
                    contenido = archivo.read()
                    print(contenido)
            except FileNotFoundError:
                return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal_campos_ingrdientes=True)

            if formReceta.nombreReceta.data == '' or formReceta.descripcion.data == '' or formReceta.totalGalletas == '' or formReceta.tiempoHornear == '' or formReceta.precioTotal == '' or request.form['pesajeGramos'] == '':
                return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, mostrar_modal_campos=True)
            else:
                cargarMateriasPrimas=DetalleReceta.query.filter_by(receta_id_receta=int(formReceta.id_receta.data)).all()
                for mp in cargarMateriasPrimas:
                    db.session.delete(mp)
                db.session.commit()

                modificaReceta = Receta.query.filter_by(id_receta=int(formReceta.id_receta.data)).first()
                modificaReceta.nombre = formReceta.nombreReceta.data
                modificaReceta.descripcion = formReceta.descripcion.data
                modificaReceta.totalGalletas = int(formReceta.totalGalletas.data)
                modificaReceta.tiempoHornear = int(formReceta.tiempoHornear.data)
                modificaReceta.precioTotal = int(formReceta.precioTotal.data)
                modificaReceta.fecha_actualiza = datetime.datetime.now()
                db.session.commit()

                with open("recetas.txt", "r",  encoding="utf-8") as file:
                    recetas = file.readlines()
                if len(recetas) != 0:
                    receta_formateada = []
                    for dato in recetas:
                        partes = dato.strip().split(", ")
                        receta = {}
                        for parte in partes:
                            if ": " in parte:
                                clave, valor = parte.split(": ", 1)
                                receta[clave] = valor
                        receta_formateada.append(receta)
                receta = Receta.query.order_by(Receta.id_receta.desc()).limit(1).first()
                for r in range(len(receta_formateada)):
                    materiasPrimas = MateriasPrimas.query.filter_by(nombre=receta_formateada[r]['ingrediente']).all()
                    id_materiaPrima = materiasPrimas[0].id_materiaPrima
                    tipoMedida = TipoMedidasMaterialPrimas.query.filter_by(descripcion=receta_formateada[r]['tipoMedida']).all()
                    id_tipoMedida = tipoMedida[0].id_medida

                    detalleReceta = DetalleReceta(cantidad=receta_formateada[r]['cantidad'],
                                                receta_id_receta=formReceta.id_receta.data,
                                                materiasprimas_id_materiaPrima=id_materiaPrima,
                                                tipomedidasmaterialprimas_id_medida=id_tipoMedida)
                    db.session.add(detalleReceta)
                    db.session.commit()
                os.remove("recetas.txt")
                return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima, cargarMateriasPrimas=cargarMateriasPrimas)
    return render_template("recetas/recetas.html", formReceta=formReceta, materiasPrimas=materiasPrimas, tipoMedidaMateriaPrima=tipoMedidaMateriaPrima,  mostrar_modal=False)
