from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100))
    admin = db.Column(db.Boolean)

class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100))
    startdate = db.Column(db.DateTime)
    serialPort = db.Column(db.String(100))

class UserContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    userId = db.Column(db.Integer, db.ForeignKey(User.id))
    containerId = db.Column(db.Integer, db.ForeignKey(Container.id))

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    containerId = db.Column(db.Integer, db.ForeignKey(Container.id))
    unit = db.Column(db.Enum('PH','EC','PSI','TEMP','PRESSURE',"LEVEL"))
    value = db.Column(db.Float)
    recordedTime = db.Column(db.DateTime)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    containerId = db.Column(db.Integer, db.ForeignKey(Container.id))
    notification = db.Column(db.String(100))
    description = db.Column(db.String(100))
    seen = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
