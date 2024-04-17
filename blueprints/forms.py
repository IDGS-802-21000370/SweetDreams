from wtforms import Form
from wtforms import StringField, TextAreaField, SelectField, RadioField, IntegerField, EmailField, BooleanField, DateField
from wtforms import validators
from blueprints.models import MateriasPrimas, Proveedor, TipoMedidasMaterialPrimas, DetalleProveedorMateria
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    usuario = StringField("Nombre de usuario", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa nombre valido")])
    contrasenia = StringField("Contraseña", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa nombre valido")])
    

class RecetaForm(Form):
    id_receta = StringField("id")
    nombreReceta = StringField("Nombre de la galleta")
    descripcion = TextAreaField("Descripcion")
    totalGalletas = StringField("Total de las galletas")
    cantidad = StringField("Cantidad")
    tiempoHornear = StringField("Tiempo en segundos")
    precioTotal = StringField("Precio total de la receta")
    #materiasPrimas = RadioField("Selecciona")
    tipoMedida = SelectField(choices=[(0, 'Selecciona'), (1,'Gramos'), (2,'Piezas'), (3, 'Mililitros'), (4,'Costales')])
class mermas(Form):
     nombre = StringField("nombre",[validators.DataRequired(message='el campo es requerido'), validators.Length(min=4,max=10,message='ingresa nombre valido')])
     fecha_creacion = StringField("fecha_creacion")
    
class ProveedorForm(Form):
    nombreEmpresa = StringField("Nombre de empresa", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa nombre valido")])
    direccion = StringField("Direccion", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa direccion valida")])
    contacto = StringField("Contacto", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa un contacto valido")])

    materia = SelectField('Materia Prima', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ProveedorForm, self).__init__(*args, **kwargs)

        materia = MateriasPrimas.query.filter_by(estatus=1).all()
        self.materia.choices = [(mtr.id_materiaPrima, mtr.nombre) for mtr in materia]
class getProveedor(Form):
    id = IntegerField('id', [validators.number_range(min=1, max=20, message='Valor no valido')])
    
    nombreEmpresa = StringField("Nombre de empresa", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa nombre valido")])
    direccion = StringField("Direccion", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa direccion valida")])
    contacto = StringField("Contacto", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa un contacto valido")])
    materia = SelectField('Materia Prima', coerce=int)
    def __init__(self, *args, **kwargs):
        super(getProveedor, self).__init__(*args, **kwargs)

        materia = MateriasPrimas.query.filter_by(estatus=1).all()
        self.materia.choices = [(mtr.id_materiaPrima, mtr.nombre) for mtr in materia]
class MateriaForm(Form):
    nombre = StringField("Nombre", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa nombre valido")])
    
    tipoMedida = SelectField('Tipo de Medida', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(MateriaForm, self).__init__(*args, **kwargs)
        # Consulta a la base de datos y Asignar las opciones al campo de lista desplegable
        medidas = TipoMedidasMaterialPrimas.query.all()
        self.tipoMedida.choices = [(medida.id_medida, medida.descripcion) for medida in medidas]
class gMateria(Form):
    id = IntegerField('id', [validators.number_range(min=1, max=20, message='Valor no valido')])
    
    nombre = StringField("Nombre", [validators.DataRequired(message="El campo es requerido"), 
                         validators.Length(min=1, max=100, message="Ingresa nombre valido")])
    tipoMedida = SelectField('Tipo de Medida', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(gMateria, self).__init__(*args, **kwargs)
        # Consulta a la base de datos y Asignar las opciones al campo de lista desplegable
        medidas = TipoMedidasMaterialPrimas.query.all()
        self.tipoMedida.choices = [(medida.id_medida, medida.descripcion) for medida in medidas]    
class CompraForm(Form):
    #tabla compra
    totalCompra = IntegerField("Total de la Compra", [validators.DataRequired(message="El campo es requerido"), validators.number_range(min=1, max=100000, message="Ingresa un valor valido")])
    #tabla detalle compra
    cantidad =IntegerField("Cantidad", [validators.DataRequired(message="El campo es requerido"),validators.number_range(min=1, max=100000, message="Ingresa un valor valido")])
    TipoMedida = StringField("Medida", [validators.DataRequired(message="El campo es requerido"), validators.Length(min=1, max=100, message="Ingresa nombre valido")])
    idMateriaPrima = SelectField('Materia Prima', coerce=int)
    idProveedor = SelectField('Proveedor', coerce=int)
    descripcion = StringField("Descripcion", [validators.DataRequired(message="El campo es requerido"), validators.Length(min=1, max=1000, message="Ingresa un valor valido")])
   
    def __init__(self, *args, **kwargs):
        super(CompraForm, self).__init__(*args, **kwargs)
        proveedores = Proveedor.query.filter_by(estatus=1).all()
        self.idProveedor.choices = [(proveedor.id_proveedor, proveedor.nombreEmpresa) for proveedor in proveedores]

        materia = DetalleProveedorMateria.query.filter_by(estatus=1).all()
        self.idMateriaPrima.choices = [(detalle.materiasprimas_id_materiaPrima, detalle.materia_prima.nombre) for detalle in materia]

class UsuarioForm(FlaskForm):
    id_usuario=IntegerField("id")
    nombre = StringField("Nombre", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa nombre valido")])
    nombreUsuario = StringField("Nombre de usuario", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa usuario valido")])
    contrasenia = PasswordField("Contraseña", validators=[
        DataRequired(message="El campo es requerido"),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    puesto = StringField("Puesto", [validators.DataRequired(message="el campo es requerido"), 
                         validators.Length(min=1, max=30, message="ingresa puesto valido")])
    roles = [("admin", "Admin"), ("usuario", "Usuario")]
    rol = SelectField("Rol", choices=roles, validators=[validators.DataRequired(message="El campo es requerido")])
