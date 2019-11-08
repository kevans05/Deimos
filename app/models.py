from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

vehicle_association_table = db.Table(
    'vehicle_association_table',
    db.Column('Vehicle_id', db.Integer, db.ForeignKey('vehicle.id')),
    db.Column('Tailboard_id', db.Integer, db.ForeignKey('tailboard.id'))
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

users_association_table = db.Table(
    'users_association_table',
    db.Column('User_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('Tailboard_id', db.Integer, db.ForeignKey('tailboard.id')),
    db.Column('Tailboard_signed_on', db.Boolean),
    db.Column('Tailboard_work_compleate', db.Boolean)
)

voltage_association_table = db.Table(
    'voltage_association_table',
    db.Column('Voltage_id', db.Integer, db.ForeignKey('voltages.id')),
    db.Column('Tailboard_id', db.Integer, db.ForeignKey('tailboard.id'))
)

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
    
       

class Tailboard(db.Model):
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

    tailboard_users = db.relationship('User', secondary=users_association_table,
                            backref=db.backref('tailboard', lazy='dynamic'))

    tailboard_voltage = db.relationship('Voltages', secondary=voltage_association_table,
                                      backref=db.backref('tailboard', lazy='dynamic'))

    def __repr__(self):
        return '<Tailboard %r>' % self.id

    def add_vehicle(self, vehicle):
        self.tailboard_vehicle.append(vehicle)

    def add_user(self, user):
        self.tailboard_users.append(user)

    def add_danger(self, danger):
        self.tailboard_dangers.append(danger)

    def add_barriers(self, barriers):
        self.tailboard_barriers.append(barriers)
    def add_voltage(self, voltage):
        self.tailboard_voltage.append(voltage)

def get_current_registared_tailboards(id):
    current_tailboards = Tailboard.query.join(users_association_table).join(User).filter((users_association_table.c.User_id == id) & (users_association_table.c.Tailboard_signed_on is not True or False) ).all()
    return(current_tailboards)

def get_current_working_tailboards(id):
    current_tailboards = Tailboard.query.join(users_association_table).join(User).filter((users_association_table.c.User_id == id) & (users_association_table.c.Tailboard_signed_on is True) & (users_association_table.c.Tailboard_work_compleate)).all()
    return(current_tailboards)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))
