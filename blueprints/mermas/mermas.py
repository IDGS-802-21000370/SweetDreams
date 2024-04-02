from flask import Blueprint, render_template, request

mermas_blueprint = Blueprint("mermas", __name__, template_folder="templates")

@mermas_blueprint.route("/mermas", methods=["GET", "POST"])
def mermas():
    if request.method=="POST":
        print("holad")
    return render_template("mermas/mermas.html")