from wtforms import Form
from wtforms import StringField, TextAreaField, SelectField, RadioField, IntegerField, EmailField, BooleanField
from wtforms import validators

class LoginForm(Form):
    usuario = StringField("Nombre de usuario", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=10, message="ingresa nombre valido")])
    contrasenia = StringField("Contraseña", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=10, message="ingresa nombre valido")])