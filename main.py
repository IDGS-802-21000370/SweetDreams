from datetime import date
import os
import datetime
from flask import Flask, request, render_template, Response, redirect, url_for
import forms
from flask_wtf.csrf import CSRFProtect
#from config import DevelopmentConfig
from flask import flash
#from models import db
app = Flask(__name__)
#app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()

@app.route("/login", methods=["GET", "POST"])
def login():
    loginForm=forms.LoginForm(request.form)
    if request.method=="POST":
        print("holad")
    return render_template("login.html", formLogin=loginForm)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

if __name__ == "__main__":
    csrf.init_app(app)
    """ db.init_app(app)
    with app.app_context():
        db.create_all() """
    app.run(debug=True)


