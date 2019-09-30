from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True)
    corporationID = db.Column(db.String(64), index=True, unique=True)
    make = db.Column(db.String(64), index=True)
    model = db.Column(db.String(64), index=True)
    enabled = db.Column(db.Boolean, index=True)

class PresentDangers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dangers = db.Column(db.String(64), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True)

class ControlBarriers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    controlBarriers = db.Column(db.String(64), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True, unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64),index=True)
    lastName = db.Column(db.String(64),index=True)
    corporateID = db.Column(db.Integer,index=True)
    email = db.Column(db.String(128), index=True, unique=True)
    tel = db.Column(db.String(128), index=True)
    supervisorEmail = db.Column(db.String(128), index=True)
    enabled = db.Column(db.Boolean, index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<Email {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

vehicles_on_tailboard = db.Table('vehicles_on_tailboard',
                                 db.Column('vehicle_id', db.Integer, db.ForeignKey('user.id')),
                                 db.Column('tailboard_id', db.Integer, db.ForeignKey('user.id'))
                                 )

class Tailboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    location = db.Column(db.String(256), index=True)
    jobSteps = db.Column(db.String(1024), index=True)
    jobHazards = db.Column(db.String(1024), index=True)
    jobProtectios = db.Column(db.String(1024), index=True)
    tailboard_vehicle = db.relationship(
        'Tailboard', secondary=vehicles_on_tailboard,
        primaryjoin=(vehicles_on_tailboard.c.vehicle_id == id),
        secondaryjoin=(vehicles_on_tailboard.c.tailboard_id == id),
        backref=db.backref('vehicles_on_tailboard', lazy='dynamic'), lazy='dynamic')

    def check_vehicles(self, tailboard):
        return self.followed.filter(
            vehicles_on_tailboard.c.tailboard_id == tailboard.id).count() > 0

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
