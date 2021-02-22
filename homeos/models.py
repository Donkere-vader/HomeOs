from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
import bcrypt


class User(db.Model, UserMixin):
    """
    # User model

    Model for all the users that have acces to the portal.
    """

    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(40), unique=True)
    password_hash = db.Column(db.LargeBinary())
    is_active = db.Column(db.Boolean)

    def __init__(self, username: str, password: str):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        print(password_hash)
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
    """

    id = db.Column(db.String, primary_key=True)
    icon = db.Column(db.String)
    control = db.Column(db.String)

    address = db.Column(db.String)  # if controlled over WiFi
    pin = db.Column(db.String)  # if controlled over GPI0 pins

    def __init__(self, id, icon, control):
        self.id, self.icon, self.control = id, icon, control

    def send(self, data):
        """
        Send to device.

        The type of data can be anything.
        For each device it can be configured sepperatly how it handles incomming data. And how it acts on it.

        For a ledstrip you would maybe want an action when "rainbow" gets sent to the device.
        """

        pass  # TODO
