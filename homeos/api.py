from .models import User
from . import db
from flask import current_app as app
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import render_template, request, redirect, jsonify
from datetime import timedelta

__version__ = "0.1.0"

# login_manager = LoginManager(app)

# @login_manager.user_loader
# def load_user(id):
#     User.query.filter_by(id=id)


@app.route("/api/v1/")
def api():
    """
    General api view
    """
    return jsonify(api_version=__version__)


@app.route("/api/v1/login", methods=["POST"])
def api_login():
    if 'username' in request.form and 'password' in request.form:
        username, password = request.form['username'], request.form['password']
    else:
        return jsonify(error="Please supply a username and password")

    user = User.query.filter_by(username=username).first()

    if user is not None and user.auth(password):
        login_user(user, remember=True, duration=timedelta(days=50))
        return jsonify(succes=True, message="Login successful")


@app.route("/api/v1/logout")
@login_required
def api_logout():
    if current_user.is_authenticated:
        logout_user(current_user)
        return jsonify(succes=True, message="Logout successful")
    return jsonify(succes=False, error="You are not logged in")


@app.route("/api/v1/set_lights", methods=["POST"])
@login_required
def set_lights():
    print(current_user.is_authenticated)
    return jsonify(succes=True, message="Lights set to red")
