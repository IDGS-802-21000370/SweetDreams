from flask import Blueprint, render_template, request

error_blueprint = Blueprint("error", __name__, template_folder="templates")

@error_blueprint.errorhandler(404)
def page_not_found(e):
    return render_template("404/404.html"),404