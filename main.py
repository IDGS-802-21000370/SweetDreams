from flask import Flask, request, render_template, Response, redirect, url_for
from blueprints.models import db
from flask_wtf.csrf import CSRFProtect
from blueprints.config import DevelopmentConfig
from blueprints.login.login import login_blueprint
from blueprints.produccion.produccion import produccion_blueprint
from blueprints.usuarios.usuario import usuario_blueprint   
from blueprints.dashboard.dashboard import dashboard_blueprint
from blueprints.ventas.venta import venta_blueprint
from blueprints.inventario.inventario import inventario_blueprint
from blueprints.recetas.receta import recetas_blueprint
from blueprints.error.error import error_blueprint
from blueprints.mermas.mermas import mermas_blueprint
from blueprints.provedores.provedor import proveedor_blueprint
from blueprints.compras.compra import compra_blueprint

app = Flask(__name__)
csrf = CSRFProtect()
app.config.from_object(DevelopmentConfig)
app.register_blueprint(login_blueprint)
app.register_blueprint(produccion_blueprint)
app.register_blueprint(usuario_blueprint)
app.register_blueprint(dashboard_blueprint)
app.register_blueprint(venta_blueprint)
app.register_blueprint(inventario_blueprint)
app.register_blueprint(recetas_blueprint)
app.register_blueprint(error_blueprint)
app.register_blueprint(mermas_blueprint)
app.register_blueprint(proveedor_blueprint)
app.register_blueprint(compra_blueprint)

if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)