from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
import bcrypt
from string import ascii_letters
import random


class User(db.Model, UserMixin):
    """
    # User model

    Model for all the users that have acces to the portal.
    """

    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(45), unique=True)
    password_hash = db.Column(db.LargeBinary())
    is_active = db.Column(db.Boolean)

    def __init__(self, username: str, password: str):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        self.username, self.password_hash, self.is_active = username, password_hash, True

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

    def __init__(self, id, icon, control, group, room):
        self.id, self.icon, self.control, self.group, self.room = id, icon, control, group, room

        # generate an API key
        aplphabet = list(ascii_letters)
        self.api_key = "".join([random.choice(aplphabet) for _ in range(45)])
        while Device.query.filter_by(api_key=self.api_key).first() is not None:
            self.api_key = "".join([random.choice(aplphabet) for _ in range(45)])

    def send(self, data):
        """
        Send to device.

        The type of data can be anything.
        For each device it can be configured sepperatly how it handles incomming data. And how it acts on it.

        For a ledstrip you would maybe want an action when "rainbow" gets sent to the device.
        """

        pass  # TODO

    def recieve(self, data):
        """
        Handle recieved data from device

        Data will be recieved through the API. The device will pass with its device_id string so that the correct function can be executed.
        """
        pass

    def turn_on(self):
        self.active = True
        db.session.commit()

    def turn_off(self):
        self.active = False
        db.session.commit()
