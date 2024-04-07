from flask_sqlalchemy import SQLAlchemy
import datetime

db=SQLAlchemy()

class TipoMedidasMaterialPrimas(db.Model):
    id_medida = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100))

class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    nombreUsuario = db.Column(db.String(100))
    contrasenia = db.Column(db.String(100))
    puesto = db.Column(db.String(100))
    rol = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)

class Compra(db.Model):
    id_compra = db.Column(db.Integer, primary_key=True)
    totalCompra = db.Column(db.String(100))
    fecha_actualiza = db.Column(db.DateTime)
    usuario_id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    usuario = db.relationship('Usuario', backref='compras')

class MateriasPrimas(db.Model):
    id_materiaPrima = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    nombre = db.Column(db.String(100))
    caducidad = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    tipomedidasmaterialprimas_id_medida = db.Column(db.Integer, db.ForeignKey('tipo_medidas_material_primas.id_medida'))
    tipo_medida = db.relationship('TipoMedidasMaterialPrimas', backref='materias_primas')

class Proveedor(db.Model):
    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombreEmpresa = db.Column(db.String(100))
    direccion = db.Column(db.String(100))
    contacto = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    estatus = db.Column(db.Integer, default=1)

class DetalleCompra(db.Model):
    id_detalleCompra = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.String(45))
    tipomedidasmaterialprimas_id_medida = db.Column(db.Integer, db.ForeignKey('tipo_medidas_material_primas.id_medida'))
    compra_id_compra = db.Column(db.Integer, db.ForeignKey('compra.id_compra'))
    materiasprimas_id_materiaPrima = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materiaPrima'))
    proveedor_id_proveedor = db.Column(db.Integer, db.ForeignKey('proveedor.id_proveedor'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)

    materia_prima = db.relationship('MateriasPrimas', backref='detalle_compra')
    proveedor = db.relationship('Proveedor', backref='detalle_compra')
    tipo_medida = db.relationship('TipoMedidasMaterialPrimas', backref='detalle_compra')

class Caja(db.Model):
    id_caja = db.Column(db.Integer, primary_key=True)
    dineroTotal = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)

class CajaRetiro(db.Model):
    id_cajaRetiro = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(300))
    dineroSacado = db.Column(db.Float)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    caja_id_caja = db.Column(db.Integer, db.ForeignKey('caja.id_caja'))
    compra_id_compra = db.Column(db.Integer, db.ForeignKey('compra.id_compra'))
    caja = db.relationship('Caja', backref='caja_retiros')
    compra = db.relationship('Compra', backref='compra_retiros')

class Receta(db.Model):
    id_receta = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(300))
    totalGalletas = db.Column(db.Integer)
    precioTotal = db.Column(db.Float)
    fecha_actualiza = db.Column(db.DateTime, default=datetime.datetime.now)

class DetalleReceta(db.Model):
    id_detalleReceta = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    receta_id_receta = db.Column(db.Integer, db.ForeignKey('receta.id_receta'))
    materiasprimas_id_materiaPrima = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materiaPrima'))
    tipomedidasmaterialprimas_id_medida = db.Column(db.Integer, db.ForeignKey('tipo_medidas_material_primas.id_medida'))
    receta = db.relationship('Receta', backref='detalles_recetas')
    materias_primas = db.relationship('MateriasPrimas', backref='detalles_recetas')
    tipo_medida = db.relationship('TipoMedidasMaterialPrimas', backref='detalles_recetas')

class TipoVenta(db.Model):
    id_tipoVenta = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100))

class Venta(db.Model):
    id_venta = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    caja_id_caja = db.Column(db.Integer, db.ForeignKey('caja.id_caja'))
    usuario_id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    caja = db.relationship('Caja', backref='ventas')
    usuario = db.relationship('Usuario', backref='ventas')

class Galleta(db.Model):
    id_galleta = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Float)
    caducidad = db.Column(db.DateTime)
    pesajeGramos = db.Column(db.Float)
    precioPieza = db.Column(db.Float)
    precioGramos = db.Column(db.Float)
    precioPaquete1 = db.Column(db.Float)
    precioPaquete2 = db.Column(db.Float)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    receta_id_receta = db.Column(db.Integer, db.ForeignKey('receta.id_receta'))
    receta = db.relationship('Receta', backref='galletas')

class DetalleVentas(db.Model):
    id_detalleVentas = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    venta_id_venta = db.Column(db.Integer, db.ForeignKey('venta.id_venta'))
    tipoventa_id_tipoVenta = db.Column(db.Integer, db.ForeignKey('tipo_venta.id_tipoVenta'))
    galleta_id_galleta = db.Column(db.Integer, db.ForeignKey('galleta.id_galleta'))
    venta = db.relationship('Venta', backref='detalles_ventas')
    tipo_venta = db.relationship('TipoVenta', backref='detalles_ventas')
    galleta = db.relationship('Galleta', backref='detalles_ventas')

class TipoMerma(db.Model):
    id_tipoMerma = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100))

class Merma(db.Model):
    id_merma = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    nombre = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    caducidad = db.Column(db.DateTime)
    tipomerma_id_tipoMerma = db.Column(db.Integer, db.ForeignKey('tipo_merma.id_tipoMerma'))
    materiasprimas_id_materiaPrima = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materiaPrima'))
    tipo_merma = db.relationship('TipoMerma', backref='mermas')
    id_detalle_galleta = db.Column(db.Integer, db.ForeignKey('detalle_galleta.id_detalle_galleta'))
    detallemateriaprima_id_detalle_materiaprima = db.Column(db.Integer, db.ForeignKey('detalle_materia_prima.id_detalle_materiaprima'))
    detalle = db.relationship('DetalleGalleta', backref='mermas')
    tipo_merma = db.relationship('TipoMerma', backref='mermas')
    materias_primas = db.relationship('MateriasPrimas', backref='mermas')
   

class DetalleMateriaPrima(db.Model):
    id_detalle_materiaprima = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    caducidad = db.Column(db.DateTime)
    mermado= db.Column(db.Integer,default=0)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materiaPrima'))
    materia_prima = db.relationship('MateriasPrimas', backref='detalle_materiaprima')
    tipo_medida_id = db.Column(db.Integer, db.ForeignKey('tipo_medidas_material_primas.id_medida'))
    tipo_medida = db.relationship('TipoMedidasMaterialPrimas', backref='detalle_materiaprima')

class DetalleGalleta(db.Model):
    id_detalle_galleta = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    caducidad = db.Column(db.DateTime)
    mermado= db.Column(db.Integer,default=0)
    galleta_id_galleta = db.Column(db.Integer, db.ForeignKey('galleta.id_galleta'))
    galleta = db.relationship('Galleta', backref='detalle_galleta')
