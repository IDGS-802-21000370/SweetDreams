from wtforms import Form
from wtforms import StringField, TextAreaField, SelectField, RadioField, IntegerField, EmailField, BooleanField
from wtforms import validators

class LoginForm(Form):
    usuario = StringField("Nombre de usuario", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=10, message="ingresa nombre valido")])
    contrasenia = StringField("Contraseña", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=10, message="ingresa nombre valido")])
    

class RecetaForm(Form):
    id_receta = StringField("id")
    nombreReceta = StringField("Nombre de la receta")
    descripcion = TextAreaField("Descripcion")
    totalGalletas = StringField("Total de las galletas")
    cantidad = StringField("Cantidad")
    #materiasPrimas = RadioField("Selecciona")
    tipoMedida = SelectField(choices=[(0, 'Selecciona'), (1,'Gramos'), (2,'Piezas'), (3, 'Mililitros'), (4,'Costales')])