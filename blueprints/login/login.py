from flask import Blueprint, render_template, request
import blueprints.forms as forms

login_blueprint = Blueprint("login", __name__, template_folder="templates")

@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    formLogin = forms.LoginForm(request.form)
    return render_template('login/login.html', formLogin=formLogin)
