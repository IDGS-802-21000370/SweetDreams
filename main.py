from datetime import date
import os
import datetime
import time
from flask import Flask, request, render_template, Response, redirect, url_for
import forms
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import flash
from models import db
from produccionGalletas import Guardar
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()

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
@app.route("/mermas", methods=["GET", "POST"])
def mermas():
    if request.method=="POST":
        print("holad")
    return render_template("mermas.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404
@app.route("/produccionGalleta", methods=["GET", "POST"])
def produccionGalletas():
    galletas_en_preparacion = []
    galletas_preparadas = []

    if request.method == "POST":
        galleta_seleccionada = request.form["galleta"]
        Guardar.galletasenpreparacion(galleta_seleccionada)
        #Guardar.mandarmostrador()
    with open("galletas_en_preparacion.txt", "r") as file:
        galletas_en_preparacion = file.readlines()
    
    with open("galletas_preparadas.txt", "r") as file:
        galletas_preparadas = file.readlines()
          
    return render_template("produccionGalleta.html", galletas_en_preparacion=galletas_en_preparacion, galletas_preparadas=galletas_preparadas)
@app.route("/enviarMostrador", methods=["POST"])
def enviarMostrador():
    Guardar.mandar_mostrador(app)
   
    return  render_template("produccionGalleta.html")
if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all() 
    app.run(debug=True)


