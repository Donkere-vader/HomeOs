from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
import bcrypt
from string import ascii_letters
import random
import requests
import json

# MANY TO MANY
user_devices = db.Table(
    'user_devices', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('device_id', db.String, db.ForeignKey('device.id'))
)

user_programs = db.Table(
    'user_programs', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('program_id', db.Integer, db.ForeignKey('program.id'))
)

user_global_programs = db.Table(
    'user_global_programs', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey("user.id")),
    db.Column('program_id', db.Integer, db.ForeignKey('global_program.id'))
)

device_programs = db.Table(
    'device_programs', db.Model.metadata,
    db.Column('device_id', db.String, db.ForeignKey('device.id')),
    db.Column('program_id', db.Integer, db.ForeignKey('program.id'))
)

global_program_devices = db.Table(
    'global_program_devices', db.Model.metadata,
    db.Column('device_id', db.String, db.ForeignKey('device.id')),
    db.Column('global_program_id', db.Integer, db.ForeignKey("global_program.id"))
)

# TABLES

class User(db.Model, UserMixin):
    """
    # User model

    Model for all the users that have acces to the portal.
    """

    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(45), unique=True)
    password_hash = db.Column(db.LargeBinary())
    is_active = db.Column(db.Boolean)
    admin = db.Column(db.Boolean, default=False)  # only me ofc 😌

    devices = db.relationship("Device", secondary=user_devices, backref="users")
    programs = db.relationship("Program", secondary=user_programs, backref="users")
    global_programs = db.relationship("GlobalProgram", secondary=user_global_programs, backref="users")

    def __init__(self, username: str, password: str, admin=False):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        self.username, self.password_hash, self.is_active, self.admin = username, password_hash, True, admin

    def get_id(self):
        return self.id

    def auth(self, password: str) -> bool:
        """
        Returns True if the password matches and False if the password doesn't match.
        """
        return bcrypt.checkpw(password.encode(), self.password_hash)


class Device(db.Model):
    """
    # Device model

    Model for all the devices.

    A ledstrip in the master bedroom that is controlled via a NodeMCU over wifi could have the following properties:

    id: ledstrip_1_masterbedroom
    icon: light
    control: node_mcu
    group: light
    room: bedroom
    """

    id = db.Column(db.String(45), primary_key=True)
    icon = db.Column(db.String(45))
    control = db.Column(db.String(45))
    group = db.Column(db.String(45))
    room = db.Column(db.String(45))
    active = db.Column(db.Boolean)

    # visual
    # Color of the tile in the dashboard (can be color of light)
    color = db.Column(db.Integer)  # HEX VALUE

    # dashboard
    name = db.Column(db.String(45))
    description = db.Column(db.Text(100))

    api_key = db.Column(db.String(45))
    address = db.Column(db.String(45))

    # relationships
    active_program = db.Column(db.String(45))
    programs = db.relationship("Program", secondary=device_programs, backref="devices")

    def __init__(self, id, icon, control, group, room):
        self.id, self.icon, self.control, self.group, self.room = id, icon, control, group, room

        # generate an API key
        aplphabet = list(ascii_letters)
        self.api_key = "".join([random.choice(aplphabet) for _ in range(45)])
        while Device.query.filter_by(api_key=self.api_key).first() is not None:
            self.api_key = "".join([random.choice(aplphabet) for _ in range(45)])

    def send(self, action, data):
        """
        Send to device.

        The type of data can be anything.
        For each device it can be configured sepperatly how it handles incomming data. And how it acts on it.

        For a ledstrip you would maybe want an action when "rainbow" gets sent to the device.
        """
        req_data = {
            "apikey": self.api_key,
            "action": action,
            "action_data": json.dumps(data)
        }

        try:
            req = requests.post(
                f"{self.address}/api/",
                req_data
            )
        except requests.exceptions.ConnectionError:
            self.active = False
            self.active_program = ""
            db.session.commit()
            return False, f"Can't connect to device '{self.name}'"
        return True, ""

    def recieve(self, data):
        """
        Handle recieved data from device

        Data will be recieved through the API. The device will pass with its device_id string so that the correct function can be executed.
        """
        pass

    def power(self, on: bool):
        succes, message = self.send(
            action="turn_on" if on else "turn_off",
            data={}
        )

        if not succes:
            return succes, message

        self.active = on
        self.active_program = ""
        db.session.commit()
        return succes, ""

    def set_color(self, color: str) -> bool:
        if self.group == 'light':
            succes, message = self.send(
                action="set_color",
                data={"color": color}
            )

            if not succes:
                return succes, message

        self.color = color
        if self.group == 'light':
            self.active_program = ""
            self.active = True

        db.session.commit()
        return True, ""

    def toggle_program(self, program_name, on=True):
        succes, message = self.send(
            action="start_program" if on else "strop_program",
            data={"program": program_name}
        )

        if not succes:
            return succes, message

        self.active_program = program_name if on else ""
        db.session.commit()
        return succes, ""


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45))

class GlobalProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45))
    active = db.Column(db.Boolean)

    devices = db.relationship("Device", secondary=global_program_devices, backref="global_programs")

    def toggle_program(self):
        self.active = not self.active
        if self.active:
            for device in self.devices:
                device.toggle_program(self.name, on=False)
        else:
            for device in self.devices:
                device.toggle_program(self.name)

        db.session.commit()
        return True, ""
