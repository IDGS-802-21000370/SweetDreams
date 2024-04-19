from flask import Blueprint, render_template, request, redirect, url_for
import blueprints.forms as forms
from blueprints.models import Galleta, Usuario
from functools import wraps
from flask_login import current_user
from flask import flash
import datetime
import os
from flask import Blueprint, flash, render_template, request
import blueprints.forms as forms
from blueprints.models import Caja, DetalleVentas, Galleta, Venta, db
import subprocess
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import blue, brown
from reportlab.lib.pagesizes import LETTER, A4
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from flask_login import login_required
from  functools import wraps
from flask_login import current_user

venta_blueprint = Blueprint("ventas", __name__, template_folder="templates")

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login.login'))
        return func(*args, **kwargs)
    return decorated_view

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
@login_required
def ventas():
    galletas=Galleta.query.all()
    galletasc = Galleta.query.filter(Galleta.cantidad < 10).all()
    if request.method=="POST":
        if 'agregarPieza' in request.form or 'agregarPaq1' in request.form or 'agregarPaq2' in request.form:
            if 'agregarPieza' in request.form:
                galletaAgregada=Galleta.query.filter_by(id_galleta=int(request.form['agregarPieza'])).first()
                id_galleta = galletaAgregada.id_galleta
                nombre = galletaAgregada.nombre
                precio = galletaAgregada.precioPieza 
                id_tipoVenta = 1
                cantidad = 1
                encontrado = False
            if 'agregarPaq1' in request.form:
                galletaAgregada=Galleta.query.filter_by(id_galleta=int(request.form['agregarPaq1'])).first()
                id_galleta = galletaAgregada.id_galleta
                nombre = galletaAgregada.nombre
                precio = galletaAgregada.precioPaquete1
                id_tipoVenta = 3
                cantidad = round(700 // galletaAgregada.pesajeGramos)
                encontrado = False
            if 'agregarPaq2' in request.form:
                galletaAgregada=Galleta.query.filter_by(id_galleta=int(request.form['agregarPaq2'])).first()
                id_galleta = galletaAgregada.id_galleta
                nombre = galletaAgregada.nombre
                precio = galletaAgregada.precioPaquete2
                id_tipoVenta = 4
                cantidad = round(1000 // galletaAgregada.pesajeGramos)
                encontrado = False
            for item in menu_items:
                if item['id_galleta'] == id_galleta and item['tipoVenta'] == id_tipoVenta:
                    item['precio'] += precio
                    if item['tipoVenta'] == 1:
                        item['cantidad'] += 1
                    elif item['tipoVenta'] == 3:
                        item['cantidad'] += round(700 // galletaAgregada.pesajeGramos)
                    elif item['tipoVenta'] == 4:
                        item['cantidad'] += round(1000 // galletaAgregada.pesajeGramos)
                        
                    cantidad = item['cantidad']
                    encontrado = True
                    id_tipoVenta = 1
                    break

            if not encontrado:
                menu_items.append({"id_galleta": id_galleta, "cantidad": cantidad, "nombre": nombre, "precio": precio, "tipoVenta": id_tipoVenta})

            totalVenta = sum(item["precio"] for item in menu_items)
            return render_template('ventas/ventas.html', galletas=galletas, menu_items=menu_items, totalVenta=totalVenta, galletasc=galletasc)
        elif 'vender' in request.form:
            totalVenta = sum(item["precio"] for item in menu_items)
            if totalVenta == 0:
                return render_template('ventas/ventas.html', galletas=galletas, modalAgregarGalleta=True)
            else:
                galletasVerificar=Galleta.query.all()
            for g in galletasVerificar:
                for item in menu_items:
                    if item['id_galleta'] == g.id_galleta and g.cantidad < item['cantidad']:
                        flash("No hay suficientes galletas de "+item['nombre'])
                        return render_template('ventas/ventas.html', galletas=galletas, totalVenta=totalVenta) 
                    else:
                        print("si hay galletas")
            venta = Venta( total = totalVenta,
                        caja_id_caja = 1,
                        usuario_id_usuario = 1)
            db.session.add(venta)
            db.session.commit()

            ventaID = Venta.query.order_by(Venta.id_venta.desc()).limit(1).first()
            for detalle in menu_items:
                detalleVenta = DetalleVentas(cantidad = detalle['cantidad'],
                                            venta_id_venta = ventaID.id_venta,
                                            tipoventa_id_tipoVenta = detalle['tipoVenta'],
                                            galleta_id_galleta = detalle['id_galleta'])
                db.session.add(detalleVenta)
                db.session.commit()
            caja = Caja.query.filter_by(id_caja=1).first()
            dineroTotalCaja = caja.dineroTotal + totalVenta
            caja.dineroTotal = dineroTotalCaja
            caja.fecha_creacion = datetime.datetime.now()
            db.session.commit()

            for item in menu_items:
                galletaRestada = Galleta.query.filter_by(id_galleta=item['id_galleta']).first()
                cantidadRestante = galletaRestada.cantidad - item['cantidad']
                galletaRestada.cantidad = cantidadRestante
                db.session.commit()
            menu_items.clear()
            return render_template('ventas/ventas.html', galletas=galletas, totalVenta=totalVenta, modalVentaRealizada=True)
        if 'quitarPieza' in request.form or 'quitarPaq1' in request.form or 'quitarPaq2' in request.form:
            if 'quitarPieza' in request.form:
                galletaAgregada=Galleta.query.filter_by(id_galleta=int(request.form['quitarPieza'])).first()
                id_galleta = galletaAgregada.id_galleta
                nombre = galletaAgregada.nombre
                precio = galletaAgregada.precioPieza
                id_tipoVenta = 1
                encontrado = False
            if 'quitarPaq1' in request.form:
                galletaAgregada=Galleta.query.filter_by(id_galleta=int(request.form['quitarPaq1'])).first()
                id_galleta = galletaAgregada.id_galleta
                nombre = galletaAgregada.nombre
                precio = galletaAgregada.precioPaquete1
                id_tipoVenta = 3
                encontrado = False
            if 'quitarPaq2' in request.form:
                galletaAgregada=Galleta.query.filter_by(id_galleta=int(request.form['quitarPaq2'])).first()
                id_galleta = galletaAgregada.id_galleta
                nombre = galletaAgregada.nombre
                precio = galletaAgregada.precioPaquete2
                id_tipoVenta = 4
                encontrado = False
            for item in menu_items:
                if item['id_galleta'] == id_galleta and item['tipoVenta'] == id_tipoVenta:
                    if item['precio'] <= 0:
                        item['precio'] = 0.0
                    else:
                        item['precio'] -= precio
                        item['cantidad'] -= 1
                        cantidad = item['cantidad']
                        encontrado = True
                        break
            totalVenta = sum(item["precio"] for item in menu_items)
            return render_template('ventas/ventas.html', galletas=galletas, menu_items=menu_items, totalVenta=totalVenta)
        if 'venderImprimir' in request.form:
            totalVenta = sum(item["precio"] for item in menu_items)
            if totalVenta == 0:
                return render_template('ventas/ventas.html', galletas=galletas, modalAgregarGalleta=True)
            else:
                venta = Venta( total = totalVenta,
                               caja_id_caja = 1,
                               usuario_id_usuario = 1)
                db.session.add(venta)
                db.session.commit()

                ventaID = Venta.query.order_by(Venta.id_venta.desc()).limit(1).first()
                for detalle in menu_items:
                    detalleVenta = DetalleVentas(cantidad = detalle['cantidad'],
                                                venta_id_venta = ventaID.id_venta,
                                                tipoventa_id_tipoVenta = detalle['tipoVenta'],
                                                galleta_id_galleta = detalle['id_galleta'])
                    db.session.add(detalleVenta)
                    db.session.commit()
                caja = Caja.query.filter_by(id_caja=1).first()
                dineroTotalCaja = caja.dineroTotal + totalVenta
                caja.dineroTotal = dineroTotalCaja
                caja.fecha_creacion = datetime.datetime.now()
                db.session.commit()

                listaTicket = []
                for item in menu_items:
                    listaTicket.append("*" + item['nombre'] + " " + "$" + str(item['precio']))
                    galletaRestada = Galleta.query.filter_by(id_galleta=item['id_galleta']).first()
                    cantidadRestante = galletaRestada.cantidad - item['cantidad']
                    galletaRestada.cantidad = cantidadRestante
                    db.session.commit()
                ticketNom = "TicketSD"
                lista = listaTicket
                canvas = Canvas("{}.pdf".format(ticketNom), pagesize=letter)
                canvas.setFont("Times-Roman", 14)
                canvas.drawString(50, canvas._pagesize[1]-60, "SweetDreams")
                canvas.drawImage("static\img\logoSweetDreams.jpeg", 350, canvas._pagesize[1]-90, width=70, height=70)
                canvas.line(50, canvas._pagesize[1]-100, 550, canvas._pagesize[1]-100)
                # Definimos la posición inicial para imprimir los elementos de la lista
                y_position = canvas._pagesize[1] - 150
                canvas.drawString(50, y_position ,"Productos comprados")
                # Iteramos sobre los elementos de la lista e imprimimos cada uno en un renglón separado
                for item in lista:
                    canvas.drawString(60, y_position -20, item)
                    y_position -= 20  # Ajusta este valor según la separación que desees entre cada elemento

                canvas.drawString(50, y_position -30, "TOTAL: ${}".format(totalVenta))

                canvas.save()
                os.system("start {}.pdf".format(ticketNom))
                menu_items.clear()
                return render_template('ventas/ventas.html', galletas=galletas, totalVenta=totalVenta, modalVentaRealizada=True)
        elif 'AceptarContrasenia' in request.form:
            abrirCaja=Caja.query.filter_by(id_caja=1).first()
            if abrirCaja.contrasenia == request.form['contrasenia']:
                return render_template('ventas/ventas.html', galletas=galletas, modalCajaValido=True)
            else:
                return render_template('ventas/ventas.html', galletas=galletas, modalCajaInvalido=True)
        elif 'retiro' in request.form:
            caja = Caja.query.filter_by(id_caja=1).first()
            dineroRetiro = request.form['montoRetiro']
            if float(dineroRetiro) >= caja.dineroTotal:
                return render_template('ventas/ventas.html', galletas=galletas, modalSinDinero=True)
            else:
                retiro = caja.dineroTotal - float(dineroRetiro)
                caja.dineroTotal = retiro
                caja.fecha_creacion = datetime.datetime.now()
                db.session.commit()
                return render_template('ventas/ventas.html', galletas=galletas, modalRetiroExitoso=True)
    return render_template('ventas/ventas.html', galletas=galletas,galletasc=galletasc)
""" =======
            
            if not encontrado:
                menu_items.append({"id_galleta": id_galleta, "nombre": nombre, "precio": precio})
                
        return render_template('ventas/ventas.html', galletas=galletas, menu_items=menu_items,galletasc=galletasc)
    
    return render_template('ventas/ventas.html', galletas=galletas,galletasc=galletasc)
>>>>>>> main """
