from .models import User, Device
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


@app.context_processor
def inject_stage_and_region():
    return dict(
        enumerate=enumerate
    )


@app.route("/")
@login_required
def index():
    return render_template("index.html", devices=Device.query.all())


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
    logout_user()
    return redirect("../../../../login")


@app.route("/dev/<device_id>", methods=["GET", "POST"])
@login_required
def dev(device_id):
    device = Device.query.get(device_id)

    if request.method == "POST":
        action = request.form["action"]

        if action == "turn_off":
            succes, message = device.power(False)
            return jsonify(succes=succes, message=message, active=device.active)
        elif action == "turn_on":
            succes, message = device.power(True)
            return jsonify(succes=succes, message=message, active=device.active)

        elif action == "set_color":
            succes, message = device.set_color(request.form['color'].replace("#", ""))
            return jsonify(succes=succes, message=message, color=device.color)

        elif action == "start_program":
            succes, message = device.start_program(request.form['program'])
            return jsonify(succes=succes, message=message, active_program=device.active_program)

    return render_template("device.html", device=device)
