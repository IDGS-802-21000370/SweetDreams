from wtforms import Form
from wtforms import StringField, TextAreaField, SelectField, RadioField, IntegerField, EmailField, BooleanField
from wtforms import validators

class LoginForm(Form):
    usuario = StringField("Nombre de usuario", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=10, message="ingresa nombre valido")])
    contrasenia = StringField("Contraseña", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=10, message="ingresa nombre valido")])
    
class UsuarioForm(Form):
    id_usuario=IntegerField("id")
    nombre = StringField("Nombre", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa nombre valido")])
    nombreUsuario = StringField("Nombre de usuario", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa usuario valido")])
    contrasenia = StringField("Contraseña", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa contraseña valida")])
    puesto = StringField("Puesto", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa puesto valido")])
    rol = StringField("Rol", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa rol valido")])