from flask import Blueprint, render_template, redirect, request, url_for
import blueprints.forms as forms
from blueprints.models import Usuario, db

usuario_blueprint = Blueprint("usuarios", __name__, template_folder="templates")

@usuario_blueprint.route("/usuario", methods=["GET", "POST"])
def usuario():
    usuarioForm = forms.UsuarioForm(request.form)
    usuarios = Usuario.query.all()
    if request.method == 'POST':
        if 'registrar' in request.form:
            nuevo_usuario = Usuario(
                nombre=usuarioForm.nombre.data,
                nombreUsuario=usuarioForm.nombreUsuario.data,
                contrasenia=usuarioForm.contrasenia.data,
                puesto=usuarioForm.puesto.data,
                rol=usuarioForm.rol.data
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
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
            usuario_actualizar = Usuario.query.filter_by(nombreUsuario=nombre_usuario).first()
            if usuario_actualizar:
                usuario_actualizar.nombre = usuarioForm.nombre.data
                usuario_actualizar.nombreUsuario = usuarioForm.nombreUsuario.data
                usuario_actualizar.contrasenia = usuarioForm.contrasenia.data
                usuario_actualizar.puesto = usuarioForm.puesto.data
                usuario_actualizar.rol = usuarioForm.rol.data
                db.session.commit()
                
            return redirect(url_for('usuarios.usuario'))
        elif 'eliminar' in request.form:
            id_usuario = int(request.form['eliminar'])
            usuario_eliminar = Usuario.query.get_or_404(id_usuario)
            db.session.delete(usuario_eliminar)
            db.session.commit()
            return redirect(url_for('usuarios.usuario'))
    return render_template("usuario/usuario.html", formUsuario=usuarioForm, usuarios=usuarios)