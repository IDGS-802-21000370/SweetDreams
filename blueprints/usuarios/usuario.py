from flask import Blueprint, render_template, redirect, request, url_for
import blueprints.forms as forms
from blueprints.models import Usuario, db
import bcrypt
from flask import flash

usuario_blueprint = Blueprint("usuarios", __name__, template_folder="templates")
def validar_contraseña_unicidad_bd(contraseña):
    contraseñas_registradas = [usuario.contrasenia for usuario in Usuario.query.all()]
    for contraseña_registrada in contraseñas_registradas:
        # Asegurarse de que tanto la contraseña como el hash estén en formato de bytes
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

@usuario_blueprint.route("/usuario", methods=["GET", "POST"])
def usuario():
    usuarioForm = forms.UsuarioForm(request.form)
    usuarios = Usuario.query.filter_by(estatus=1).all()
    if request.method == 'POST':
        if 'registrar' in request.form:
            contraseña_ingresada = usuarioForm.contrasenia.data
            """ if not validar_contraseña_unicidad_bd(contraseña_ingresada):
                flash('La contraseña ingresada ya está en uso.', 'error') """
            """ if not validar_contraseña_unicidad_txt(contraseña_ingresada):
                flash('La contraseña ingresada no es segura.', 'error')
            else: """
                # Si pasa ambas validaciones, procede a registrar el nuevo usuario
            #password_hash = bcrypt.hashpw(contraseña_ingresada.encode('utf-8'), bcrypt.gensalt())
            nuevo_usuario = Usuario(
                nombre=usuarioForm.nombre.data,
                nombreUsuario=usuarioForm.nombreUsuario.data,
                contrasenia=usuarioForm.contrasenia.data,
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
            if not validar_contraseña_unicidad_txt(contraseña_ingresada):
                flash('La contraseña ingresada no es segura.', 'error')
            else:
                if usuario_actualizar:
                    usuario_actualizar.nombre = usuarioForm.nombre.data
                    usuario_actualizar.nombreUsuario = usuarioForm.nombreUsuario.data
                    usuario_actualizar.puesto = usuarioForm.puesto.data
                    usuario_actualizar.rol = usuarioForm.rol.data
                    usuario_actualizar.contrasenia = usuarioForm.contrasenia.data
                    """  if nueva_contrasenia:
                        # Hashea la nueva contraseña antes de guardarla
                        password_hash = bcrypt.hashpw(nueva_contrasenia.encode('utf-8'), bcrypt.gensalt())
                        usuario_actualizar.contrasenia = password_hash """
                    db.session.commit()
                
            return redirect(url_for('usuarios.usuario'))
        elif 'eliminar' in request.form:
            id_usuario = int(request.form['eliminar'])
            usuario_eliminar = Usuario.query.get_or_404(id_usuario)
            usuario_eliminar.estatus = 0
            db.session.commit()
            return redirect(url_for('usuarios.usuario'))
    return render_template("usuario/usuario.html", formUsuario=usuarioForm, usuarios=usuarios)