from .models import User, Device, GlobalProgram
from flask import current_app as app
from flask import render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import timedelta
from . import db
from .functions import print_html


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
        enumerate=enumerate,
        print_html=print_html,
        len=len
    )


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # db.session.add(User("cassis", "password", admin=True))
    # db.session.commit()

    if request.method == "POST":
        username, password = request.form['username'], request.form['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and user.auth(password):
            login_user(user, remember=True, duration=timedelta(days=100))
            return redirect("../../../../")

        return render_template("public/login.html", error="Invalid username or password")
    return render_template("public/login.html")

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_panel():
    if not current_user.admin:
        return redirect("../../../../")
    if request.method == "POST":
        code = request.form['code']
        code = [line for line in code.split("\r\n") if line]

        for line in code:
            exec(line)

        return f"<h3>submitted:</h3><code>{code}</code>"
    return render_template("admin.html")

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
            succes, message = device.toggle_program(request.form['program'])
            return jsonify(succes=succes, message=message, active_program=device.active_program)

    return render_template("device.html", device=device)


@app.route("/programs", methods=["GET", "POST"])
@login_required
def programs():
    if request.method == "POST":
        action = request.form['action']

        if action == 'toggle_program':
            program = GlobalProgram.query.filter_by(id=request.form['program_id']).first()
            succes, message = program.toggle_program()
            return jsonify(succes=succes, message=message, active=program.active)

    return render_template("programs.html")


@app.route("/new_user", methods=["GET", "POST"])
@login_required
def new_user():
    if not current_user.admin:
        return redirect("../../../../")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template("new_user.html", error="Password's dont match")

        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        return f"<span>User \"{username}\" created</span>"

    return render_template("new_user.html")
