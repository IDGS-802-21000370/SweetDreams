from flask import Flask, request, render_template, Response, redirect, url_for
from requests import Session
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
from blueprints.materia.materia import materiaprima_blueprint
from blueprints.models import Usuario, db
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView

app = Flask(__name__)
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rol == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated and current_user.rol == 'usuario':
            return redirect(url_for('ventas.ventas')) 
        else:
            return redirect(url_for('logout'))

    def render(self, template, **kwargs):
        return redirect(url_for('ventas.ventas'))

admin = Admin(name='SweetDreams', index_view=MyAdminIndexView())
admin = Admin(index_view=MyAdminIndexView(name='usuario'))
admin.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

app.register_blueprint(login_blueprint)
app.config.from_object(DevelopmentConfig)
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
app.register_blueprint(materiaprima_blueprint)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404/404.html'), 404

if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)