from app import db, app
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from time import time

import jwt

vehicle_association_table = db.Table(
    'vehicle_association_table',
    db.Column('Vehicle_id', db.Integer, db.ForeignKey('vehicle.id')),
    db.Column('Tailboard_id', db.Integer, db.ForeignKey('tailboard.id')),
)

dangers_association_table = db.Table(
    'dangers_association_table',
    db.Column('Dangers_id', db.Integer, db.ForeignKey('dangers.id')),
    db.Column('Tailboard_id', db.Integer, db.ForeignKey('tailboard.id'))
)


barriers_association_table = db.Table(
    'barriers_association_table',
    db.Column('Barriers_id', db.Integer, db.ForeignKey('barriers.id')),
    db.Column('Tailboard_id', db.Integer, db.ForeignKey('tailboard.id'))
)


voltage_association_table = db.Table(
    'voltage_association_table',
    db.Column('Voltage_id', db.Integer, db.ForeignKey('voltages.id')),
    db.Column('Tailboard_id', db.Integer, db.ForeignKey('tailboard.id'))
)


class Tailboard_Users(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    
    tailboard_id = db.Column(db.Integer, db.ForeignKey('tailboard.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    sign_on_time = db.Column(db.DateTime, index=True) 
    sign_off_time = db.Column(db.DateTime, index=True)

    def get_refuse_tailboard_token(self, expires_in=600):
        return (jwt.encode(
            {'refuseTailboardEmail': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8'))

    @staticmethod
    def verify_refuse_tailboard_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['refuseTailboardEmail']
        except:
            return
        return Tailboard_Users.query.get(id)

    def get_accept_tailboard_token(self, expires_in=600):
        return(jwt.encode(
                    {'joinTailboardEmail': self.id, 'exp': time() + expires_in},
                    app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8'))

    @staticmethod
    def verify_join_tailboard_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                    algorithms=['HS256'])['joinTailboardEmail']
        except:
            return
        return Tailboard_Users.query.get(id)

    def get_sign_off_token(self, expires_in=600):
        return(jwt.encode(
                    {'signOffTailboardEmail': self.id, 'exp': time() + expires_in},
                    app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8'))

    @staticmethod
    def verify_sign_off_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                    algorithms=['HS256'])['signOffTailboardEmail']
        except:
            return
        return Tailboard_Users.query.get(id)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True)
    corporationID = db.Column(db.String(64), index=True, unique=True)
    make = db.Column(db.String(64), index=True)
    model = db.Column(db.String(64), index=True)
    enabled = db.Column(db.Boolean, index=True)

class Dangers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dangers = db.Column(db.String(64), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True)

class Voltages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voltage = db.Column(db.String(64), index=True)
    numberOfPhases = db.Column(db.Integer, index=True)
    numberOfWires = db.Column(db.Integer, index=True)
    enabled = db.Column(db.Boolean, index=True)

class Barriers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    controlBarriers = db.Column(db.String(64), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True)


class Tailboard(db.Model):
    __tablename__ = 'tailboard'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    location = db.Column(db.String(256), index=True)
    jobSteps = db.Column(db.String(1024), index=True)
    presentVoltages = db.Column(db.String(256), index=True)
    jobHazards = db.Column(db.String(1024), index=True)
    jobProtectios = db.Column(db.String(1024), index=True)

    tailboard_vehicle = db.relationship('Vehicle', secondary=vehicle_association_table,
                            backref=db.backref('tailboard', lazy='dynamic'))

    tailboard_dangers = db.relationship('Dangers', secondary=dangers_association_table,
                            backref=db.backref('tailboard', lazy='dynamic'))

    tailboard_barriers = db.relationship('Barriers', secondary=barriers_association_table,
                            backref=db.backref('tailboard', lazy='dynamic'))

    tailboard_voltage = db.relationship('Voltages', secondary=voltage_association_table,
                            backref=db.backref('tailboard', lazy='dynamic'))

    tailboard_user = db.relationship('Tailboard_Users', backref='tailboard',
                                     primaryjoin=id == Tailboard_Users.tailboard_id)


    def __repr__(self):
        return '<Tailboard %r>' % self.id

    def add_vehicle(self, vehicle):
        self.tailboard_vehicle.append(vehicle)

    def add_danger(self, danger):
        self.tailboard_dangers.append(danger)

    def add_barriers(self, barriers):
        self.tailboard_barriers.append(barriers)

    def add_voltage(self, voltage):
        self.tailboard_voltage.append(voltage)

    def add_user(self, user):
        tailboard_users = Tailboard_Users(tailboard_id=self.id, user_id=user.id)
        self.tailboard_user.append(tailboard_users)
        user.user_tailboard.append(tailboard_users)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64),index=True)
    lastName = db.Column(db.String(64),index=True)
    corporateID = db.Column(db.Integer,index=True)
    email = db.Column(db.String(128), index=True, unique=True)
    tel = db.Column(db.String(128), index=True)
    supervisorEmail = db.Column(db.String(128), index=True)
    enabled = db.Column(db.Boolean, index=True)
    password_hash = db.Column(db.String(128))

    user_tailboard = db.relationship('Tailboard_Users', backref='user',
                                     primaryjoin=id == Tailboard_Users.user_id)
    
    def __repr__(self):
        return '<Email {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
                return jwt.encode(
                    {'reset_password': self.id, 'exp': time() + expires_in},
                    app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                    algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

