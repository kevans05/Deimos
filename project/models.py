from project import db
from project import login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    corporationID = db.Column(db.String(64), index=True, unique=True)
    make = db.Column(db.String(64), index=True, unique=True)
    model = db.Column(db.String(64), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True,unique=True)

class presentDangers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dangers = db.Column(db.String(64), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True, unique=True)

class controlsBarriers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    controlsBarriers = db.Column(db.String(64), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True, unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64),index=True,unique=True)
    lastName = db.Column(db.String(64),index=True,unique=True)
    corporateID = db.Column(db.Integer,index=True,unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    tel = db.Column(db.String(128), index=True, unique=True)
    supervisorEmail = db.Column(db.String(128), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True,unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<Email {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


staff_on_tailboard = db.Table('staff_on_tailboard',
                              db.Column('staff_on_tailboard_id', db.Integer, db.ForeignKey('user.id')),
                              db.Column('staff_on_tailboard_id', db.Integer, db.ForeignKey('user.id'))
                              )

vehicle_on_tailboard = db.Table('vehicle_on_tailboard',
                              db.Column('vehicle_on_tailboard_id', db.Integer, db.ForeignKey('vehicle.id')),
                              db.Column('vehicle_on_tailboard_id', db.Integer, db.ForeignKey('vehicle.id'))
                              )

presentDangers_on_tailboard = db.Table('presentDangers_on_tailboard',
                              db.Column('presentDangers_on_tailboard_id', db.Integer, db.ForeignKey('presentDangers.id')),
                              db.Column('presentDangers_on_tailboard_id', db.Integer, db.ForeignKey('presentDangers.id'))
                              )

controlsBarriers_on_tailboard = db.Table('controlsBarriers_on_tailboard',
                              db.Column('controlsBarriers_on_tailboard_id', db.Integer, db.ForeignKey('controlsBarriers.id')),
                              db.Column('controlsBarriers_on_tailboard_id', db.Integer, db.ForeignKey('controlsBarriers.id'))
                              )

class tailboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    staff_on_site = db.relationship(
        'User', secondary=staff_on_tailboard,
        primaryjoin=(staff_on_tailboard.c.staff_on_tailboard_id == id),
        secondaryjoin=(staff_on_tailboard.c.staff_on_tailboard_id == id),
        backref=db.backref('staff_on_tailboard_id', lazy='dynamic'), lazy='dynamic')

    vehicle_on_site = db.relationship(
        'vehicle', secondary=vehicle_on_tailboard,
        primaryjoin=(vehicle_on_tailboard.c.vehicle_on_tailboard_id == id),
        secondaryjoin=(vehicle_on_tailboard.c.vehicle_on_tailboard_id == id),
        backref=db.backref('vehicle_on_tailboard_id', lazy='dynamic'), lazy='dynamic')

    presentDangers__on_site = db.relationship(
        'presentDangers', secondary=presentDangers_on_tailboard,
        primaryjoin=(presentDangers_on_tailboard.c.presentDangers_on_tailboard_id == id),
        secondaryjoin=(presentDangers_on_tailboard.c.presentDangers_on_tailboard_id == id),
        backref=db.backref('vehicle_on_tailboard_id', lazy='dynamic'), lazy='dynamic')

    controlsBarriers__on_site = db.relationship(
        'controlsBarriers', secondary=controlsBarriers_on_tailboard,
        primaryjoin=(controlsBarriers_on_tailboard.c.controlsBarriers_on_tailboard_id == id),
        secondaryjoin=(controlsBarriers_on_tailboard.c.controlsBarriers_on_tailboard_id == id),
        backref=db.backref('vehicle_on_tailboard_id', lazy='dynamic'), lazy='dynamic')

    def add_staff(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def remove_staff(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_on_site(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


@login.user_loader
def load_user(id):
    return User.query.get(int(id))



