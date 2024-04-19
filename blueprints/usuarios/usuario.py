from flask import Blueprint, render_template, redirect, request, url_for, current_app
import blueprints.forms as forms
from blueprints.models import Usuario, db
import bcrypt
from flask import flash
import re
from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
import datetime as datetime
import jwt
from  functools import wraps
from flask_login import current_user

usuario_blueprint = Blueprint("usuarios", __name__, template_folder="templates")
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            return render_template('404/404.html')
        return func(*args, **kwargs)
    return decorated_view


@usuario_blueprint.route("/usuario", methods=["GET", "POST"])
@admin_required
def usuario():
    usuarioForm = forms.UsuarioForm(request.form)
    usuarios = Usuario.query.filter_by(estatus=1).all()
    if request.method == 'POST':
        if 'registrar' in request.form:
            contraseña_ingresada = usuarioForm.contrasenia.data
            es_segura, mensaje = validar_contraseña_segura(contraseña_ingresada)
            if not es_segura:
                flash(mensaje, 'warning')
                """ elif not validar_contraseña_unicidad_bd(contraseña_ingresada):
                flash('La contraseña ingresada ya está en uso.', 'warning') """
            elif not validar_contraseña_unicidad_txt(contraseña_ingresada):
                flash('La contraseña ingresada no es segura.', 'warning')
            else:
                password_hash = bcrypt.hashpw(contraseña_ingresada.encode('utf-8'), bcrypt.gensalt())
                nuevo_usuario = Usuario(
                    nombre=usuarioForm.nombre.data,
                    nombreUsuario=usuarioForm.nombreUsuario.data,
                    contrasenia=password_hash,
                    puesto=usuarioForm.puesto.data,
                    rol=usuarioForm.rol.data
                )
                db.session.add(nuevo_usuario)
                db.session.commit()
                flash('Usuario registrado con éxito!', 'success')
                return redirect(url_for('usuarios.usuario'))
            
        elif 'accion' in request.form:
            accion, usuario_id_str = request.form['accion'].split('_', 1)
            usuario_id = int(usuario_id_str)
            if accion == 'editar':
                usuario_editar = Usuario.query.get_or_404(usuario_id)
                usuarioForm.id_usuario.data=usuario_editar.id_usuario
                usuarioForm.nombre.data = usuario_editar.nombre
                usuarioForm.nombreUsuario.data = usuario_editar.nombreUsuario
                usuarioForm.contrasenia.data = usuario_editar.contrasenia
                usuarioForm.puesto.data = usuario_editar.puesto
                usuarioForm.rol.data = usuario_editar.rol
                return render_template("usuario/usuario.html", formUsuario=usuarioForm, usuarios=usuarios)
        elif 'actualizar' in request.form:
            nombre_usuario = usuarioForm.nombreUsuario.data
            contraseña_ingresada = usuarioForm.contrasenia.data
            usuario_actualizar = Usuario.query.filter_by(nombreUsuario=nombre_usuario).first()
            es_segura, mensaje = validar_contraseña_segura(contraseña_ingresada)
            if not es_segura:
                flash(mensaje, 'warning')
            elif not validar_contraseña_unicidad_bd(contraseña_ingresada):
                flash('La contraseña ingresada ya está en uso.', 'warning')
            elif not validar_contraseña_unicidad_txt(contraseña_ingresada):
                flash('La contraseña ingresada no es segura.', 'warning')
            else:
                if usuario_actualizar:
                    usuario_actualizar.nombre = usuarioForm.nombre.data
                    usuario_actualizar.nombreUsuario = usuarioForm.nombreUsuario.data
                    usuario_actualizar.puesto = usuarioForm.puesto.data
                    usuario_actualizar.rol = usuarioForm.rol.data
                    nueva_contrasenia = usuarioForm.contrasenia.data
                    if nueva_contrasenia:
                        password_hash = bcrypt.hashpw(nueva_contrasenia.encode('utf-8'), bcrypt.gensalt())
                        usuario_actualizar.contrasenia = password_hash
                    db.session.commit()
                    flash('Usuario actualizado correctamente', 'success')
                
            return redirect(url_for('usuarios.usuario'))
        elif 'eliminar' in request.form:
            id_usuario = int(request.form['eliminar'])
            usuario_eliminar = Usuario.query.get_or_404(id_usuario)
            usuario_eliminar.estatus = 0
            db.session.commit()
            return redirect(url_for('usuarios.usuario'))
    return render_template("usuario/usuario.html", formUsuario=usuarioForm, usuarios=usuarios)

def validar_contraseña_segura(contraseña):
    if len(contraseña) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search("[A-Z]", contraseña):
        return False, "La contraseña debe incluir al menos una letra mayúscula."
    if not re.search("[a-z]", contraseña):
        return False, "La contraseña debe incluir al menos una letra minúscula."
    if not re.search("[0-9]", contraseña):
        return False, "La contraseña debe incluir al menos un número."
    if not re.search("[@_!#$%^&*()<>?/|}{~:.,]", contraseña):
        return False, "La contraseña debe incluir al menos un carácter especial."
    return True, "La contraseña es segura."

def validar_contraseña_unicidad_bd(contraseña):
    contraseñas_registradas = [usuario.contrasenia for usuario in Usuario.query.all()]
    for contraseña_registrada in contraseñas_registradas:
        contraseña_bytes = contraseña.encode('utf-8')
        hash_bytes = contraseña_registrada.encode('utf-8')
        if bcrypt.checkpw(contraseña_bytes, hash_bytes):
            return False
    return True

def validar_contraseña_unicidad_txt(contraseña):
    with open('contraseñas.txt', 'r') as file:
        contraseñas = file.readlines()
        contraseñas = [contraseña.strip() for contraseña in contraseñas]
        return contraseña not in contraseñas
