from flask import Flask, Blueprint, render_template, request, url_for, redirect
import blueprints.forms as forms
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from blueprints.models import Usuario
import bcrypt
from flask import flash

login_blueprint = Blueprint("login", __name__, template_folder="templates")

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    formLogin = forms.LoginForm()
    if formLogin.validate_on_submit():
        nombreUsuario = formLogin.usuario.data
        contrasenia = formLogin.contrasenia.data.encode('utf-8')  
        user = Usuario.query.filter_by(nombreUsuario=nombreUsuario).first()

        if user and bcrypt.checkpw(contrasenia, user.contrasenia.encode('utf-8')):
            if user.estatus == 1:
                login_user(user)
                if user.rol == 'admin':
                    return redirect(url_for('ventas.ventas'))
                elif user.rol == 'usuario':
                    return redirect(url_for('ventas.ventas'))
                else:
                    return redirect(url_for('login.login'))
            else:
                flash('El usuario no está activado', 'error')
                return redirect(url_for('login.login')) 
        else:
            flash('Nombre de usuario o contraseña incorrecta.', 'error')
            return redirect(url_for('login.login')) 

    return render_template('login/login.html', formLogin=formLogin)

@login_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.logout'))

@login_blueprint.route('/venta')
@login_required
def user():
    return render_template('ventas/ventas.html')


 