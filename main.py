from datetime import date
import os
import datetime
from flask import Flask, request, render_template, Response, redirect, url_for
import forms
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import flash
from models import db, Proveedor, Compra, DetalleCompra
import proveedor
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()
MPrima = []
MPrimaTexto = []

@app.route("/login", methods=["GET", "POST"])
def login():
    loginForm=forms.LoginForm(request.form)
    if request.method=="POST":
        print("holad")
    return render_template("login.html", formLogin=loginForm)

@app.route("/galletas", methods=["GET", "POST"])
def galletas():
    if request.method=="POST":
        print("holad")
    return render_template("galletas.html")

@app.route("/proveedores", methods=["GET", "POST"])
def proveedorIndex():
    proveedores = Proveedor.query.filter_by(estatus=1).all()
    
    if request.method == "POST":
        if 'buttonP' in request.form:
            #Alerta para eliminar
            proveedor.eliminarP()
            return redirect(url_for('proveedorIndex'))
        
    return render_template("proveedor/proveedor.html", Proveedor=proveedores)

@app.route("/proveedoresForm", methods=["GET", "POST"])
def prooveedorForm():
    prvdForm=forms.ProveedorForm(request.form)
    if request.method=="POST":
        if request.form['btnPrv'] == "btnRegistrarPrv":
            #Alerta para registrar
            proveedor.indexP()
            return redirect(url_for('proveedorIndex'))
            
    return render_template("proveedor/proveedorForm.html", formProveedor=prvdForm)

@app.route("/proveedoresUpdate", methods=["GET", "POST"])
def prooveedorUpdate():
    prvdForm=forms.getProveedor(request.form)
    if request.method=='GET':
        id=request.args.get('id')
        prvdA=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
        prvdForm.id.data=request.args.get('id')
        prvdForm.nombreEmpresa.data=prvdA.nombreEmpresa
        prvdForm.direccion.data=prvdA.direccion
        prvdForm.contacto.data=prvdA.contacto
    if request.method=="POST":
        #Alerta para editar
        id=prvdForm.id.data
        prvd=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
        prvd.nombreEmpresa=prvdForm.nombreEmpresa.data
        prvd.direccion=prvdForm.direccion.data
        prvd.contacto=prvdForm.contacto.data
        db.session.add(prvd)
        db.session.commit()
        return redirect(url_for('proveedorIndex'))
    return render_template("proveedor/proveedorM.html", formProveedor=prvdForm)

@app.route("/compras", methods=["GET", "POST"])
def compraIndex():
    compras = Compra.query.all()
        
    return render_template("compra/compra.html", Compra=compras)

@app.route("/detalleCompra", methods=["GET", "POST"])
def detalleCompraIndex():
    if request.method=='GET':
        id=request.args.get('id')
        dCompras = DetalleCompra.query.filter_by(compra_id_compra=id).all()
        
    return render_template("compra/detalleCompra.html", dCompra=dCompras)

@app.route("/compraForm", methods=["GET", "POST"])
def compraForm():
    crpForm=forms.CompraForm(request.form)
    global MPrima
    global MPrimaTexto
    
    if request.method=="POST":
        if request.form['buttonMP'] == "btnAgregarMP":
            cantidad=crpForm.cantidad.data
            tipoMP_id = crpForm.idTipoMedida.data
            tipoMP_valor = dict(crpForm.idTipoMedida.choices).get(tipoMP_id)
            materiaprima_id = crpForm.idMateriaPrima.data
            materiaprima_valor = dict(crpForm.idMateriaPrima.choices).get(materiaprima_id)
            prvd_id = crpForm.idProveedor.data
            prvd_valor = dict(crpForm.idProveedor.choices).get(prvd_id)
            print(tipoMP_valor)
            MPrima.append({ 
                           'cantidad': cantidad, 
                           'tipoMP':tipoMP_id, 
                           'materiaprima': materiaprima_id, 
                           'prvd':prvd_id
                           }
            )
            MPrimaTexto.append({ 
                           'cantidad': cantidad, 
                           'tipoMP':tipoMP_valor, 
                           'materiaprima': materiaprima_valor, 
                           'prvd':prvd_valor
                           }
            )

        if request.form['buttonMP'] == "btnQuitarMP":
            indexEliminar = request.form.getlist('eliminar[]')
            indexEliminar = [int(index) for index in indexEliminar]
            MPrima = [materiap for i, materiap in enumerate(MPrima, 1) if i not in indexEliminar]
        
        if request.form['buttonMP'] == "btnLimpiarMP":
            MPrima.clear()

        #Alerta para Registrar
        if request.form['buttonMP'] == "btnRegistrarMP":
            #tabla compra
            prvd=Compra(totalCompra=crpForm.totalCompra.data, fecha_actualiza = crpForm.fecha_actualiza.data, usuario_id_usuario = 1)
                #Cambiar id_usuario por id del usuario loggeado
            db.session.add(prvd)
            db.session.commit()
            
            #tabla detalle compra
            idCompra = db.session.query(db.func.max(Compra.id_compra)).scalar()
            for elemento in MPrima:
                cantidad = elemento['cantidad']
                tipoMP_id = elemento['tipoMP']
                materiaprima_id = elemento['materiaprima']
                prvd_id = elemento['prvd']
        
                detalle = DetalleCompra(cantidad=cantidad, tipomedidasmaterialprimas_id_medida=tipoMP_id, 
                                        compra_id_compra=idCompra, materiasprimas_id_materiaPrima=materiaprima_id, 
                                        proveedor_id_proveedor=prvd_id)
        
                db.session.add(detalle)
                db.session.commit()
            MPrima.clear()
            MPrimaTexto.clear()

    return render_template("compra/compraForm.html", formCompra=crpForm, MPrima=MPrimaTexto)
        
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all() 
    app.run(debug=True)


