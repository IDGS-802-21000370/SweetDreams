from flask import Flask, Blueprint, render_template, request, url_for, redirect
import blueprints.forms as forms
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from blueprints.models import Usuario, db
import bcrypt
from flask import flash
import logging
from datetime import datetime

login_blueprint = Blueprint("login", __name__, template_folder="templates")

logging.basicConfig(filename='login_logs.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    formLogin = forms.LoginForm()
    if formLogin.validate_on_submit():
        nombreUsuario = formLogin.usuario.data
        contrasenia = formLogin.contrasenia.data.encode('utf-8')  
        user = Usuario.query.filter_by(nombreUsuario=nombreUsuario).first()
        #if user and user.contrasenia:
        if user:
            if user.intentos < 3:
                #if bcrypt.checkpw(contrasenia, user.contrasenia.encode('utf-8')):
                if user and user.contrasenia:
                    if user.estatus == 1:
                        user.intentos = 0
                        user.ultimo_inicio_sesion = datetime.now()
                        db.session.commit()
                        logging.info(f'Inicio de sesión exitoso para el usuario: {nombreUsuario}')
                        login_user(user)
                        if user.rol == 'admin':
                            return redirect(url_for('admin.index'))
                        elif user.rol == 'usuario':
                            return redirect(url_for('admin.index'))
                    else:
                        flash('El usuario no está activado', 'warning')
                        logging.warning(f'Intento de inicio de sesión fallido para el usuario desactivado: {nombreUsuario}')
                else:
                    user.intentos += 1
                    db.session.commit()
                    flash('Nombre de usuario o contraseña incorrecta.', 'warning')
                    logging.warning(f'Intento de inicio de sesión fallido para el usuario: {nombreUsuario}')
            else:
                user.estatus = 0  # Bloquear usuario
                db.session.commit()
                flash('Este usuario ha sido bloqueado por intentos fallidos', 'warning')
        else:
            flash('Nombre de usuario o contraseña incorrecta.', 'warning')
            logging.warning(f'Intento de inicio de sesión fallido para el usuario: {nombreUsuario}')
        
        return redirect(url_for('login.login')) 

    return render_template('login/login.html', formLogin=formLogin)

@login_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.login'))

 