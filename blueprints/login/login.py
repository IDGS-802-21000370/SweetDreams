from flask import Flask, Blueprint, render_template, request, url_for, redirect
import blueprints.forms as forms
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from blueprints.models import Usuario

login_blueprint = Blueprint("login", __name__, template_folder="templates")

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    formLogin = forms.LoginForm()
    if formLogin.validate_on_submit():
        nombreUsuario = formLogin.usuario.data
        contrasenia = formLogin.contrasenia.data
        user = Usuario.query.filter_by(nombreUsuario=nombreUsuario).first()
        if user and user.contrasenia == contrasenia:
            if user.estatus == 1:
                login_user(user)
                if user.rol == 'admin':
                    return redirect(url_for('login.admin'))
                elif user.rol == 'usuario':
                    return redirect(url_for('login.user'))
                else:
                    return redirect(url_for('login.login'))
            else:
                return 'El usuario no está activado'
        else:
            return 'Usuario o contraseña inválidos'
    return render_template('ventas/ventas.html', formLogin=formLogin)

@login_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.logout'))

@login_blueprint.route('/user')
@login_required
def user():
    return render_template('layoutPrincipal.html')

@login_blueprint.route('/admin')
@login_required
def admin():
    return render_template('layoutPrincipal.html')

 