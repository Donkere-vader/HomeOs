from .models import User
from flask import current_app as app
from flask import render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import timedelta
from . import db


login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()


@login_manager.unauthorized_handler
def unauth_handler():
    return redirect("../../../../login")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username, password = request.form['username'], request.form['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and user.auth(password):
            login_user(user, remember=True, duration=timedelta(days=100))
            return redirect("../../../../")

        return render_template("public/login.html", error="Invalid username or password")
    return render_template("public/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user(current_user)
    return redirect("../../../../login")


@app.route("/dev/<device_id>")
@login_required
def dev(device_id):
    return jsonify(device_id=device_id)