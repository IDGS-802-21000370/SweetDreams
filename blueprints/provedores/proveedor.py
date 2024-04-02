import blueprints.forms as forms
from flask import Flask, request, render_template, Response, redirect, url_for
from blueprints.models import db, Proveedor


def indexP():
    prvd_form=forms.ProveedorForm(request.form)
    prvd=Proveedor(nombreEmpresa=prvd_form.nombreEmpresa.data, direccion = prvd_form.direccion.data, contacto = prvd_form.contacto.data)
    db.session.add(prvd)
    db.session.commit()

def eliminarP():
    id = request.form['buttonP']
    prvd=db.session.query(Proveedor).filter(Proveedor.id_proveedor==id).first()
    prvd.estatus = 0
    db.session.add(prvd)
    db.session.commit()
