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

# vehicles_on_tailboard = db.Table(
#     'vehicles_on_tailboard',
#     db.Column('vehicle_on_tailboard_id', db.Integer, db.ForeignKey('vehicle.id')),
#     db.Column('vehicle_added_to_tailboard_id', db.Integer, db.ForeignKey('vehicle.id'))
# )
# 
# present_dangers_on_tailboard = db.Table(
#     'present_dangers_on_tailboard',
#     db.Column('present_danger_on_tailboard_id', db.Integer, db.ForeignKey('presentDangers.id')),
#     db.Column('present_danger_added_to_tailboard_id', db.Integer, db.ForeignKey('presentDangers.id'))
# )
# 
# controls_barriers_on_tailboard = db.Table(
#     'controls_barriers_on_tailboard',
#     db.Column('controls_barrier_on_tailboard_id', db.Integer, db.ForeignKey('controlsBarriers.id')),
#     db.Column('controls_barrier_added_to_tailboard_id', db.Integer, db.ForeignKey('controlsBarriers.id'))
# )
# 
# staffs_on_tailboard = db.Table(
#     'staffs_on_tailboard',
#     db.Column('staff_on_tailboard_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('staff_added_to_tailboard_id', db.Integer, db.ForeignKey('user.id'))
# )
# 
# class tailboard(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     voltagesPresent = db.Column(db.String(140))
#     location = db.Column(db.String(140))
#     jobSteps = db.Column(db.String(140))
#     hazards = db.Column(db.String(140))
#     barrriersMitigation 
# 
#     vehicle_added_to_tailboard = db.relationship(
#         'vehicle', secondary=vehicles_on_tailboard,
#         primaryjoin=(vehicles_on_tailboard.c.vehicle_on_tailboard_id == id),
#         secondaryjoin=(vehicles_on_tailboard.c.vehicle_added_to_tailboard_id == id),
#         backref=db.backref('vehicles_on_tailboard', lazy='dynamic'), lazy='dynamic')
# 
#     present_danger_added_to_tailboard = db.relationship(
#         'presentDangers', secondary=present_dangers_on_tailboard,
#         primaryjoin=(present_dangers_on_tailboard.c.present_danger_on_tailboard_id == id),
#         secondaryjoin=(present_dangers_on_tailboard.c.present_danger_added_to_tailboard_id == id),
#         backref=db.backref('present_dangers_on_tailboard', lazy='dynamic'), lazy='dynamic')
# 
#     controls_barrier_added_to_tailboard = db.relationship(
#         'controlsBarriers', secondary=controls_barriers_on_tailboard,
#         primaryjoin=(controls_barriers_on_tailboard.c.controls_barrier_on_tailboard_id == id),
#         secondaryjoin=(controls_barriers_on_tailboard.c.controls_barrier_added_to_tailboard_id == id),
#         backref=db.backref('controls_barriers_on_tailboard', lazy='dynamic'), lazy='dynamic')
# 
#     staff_added_to_tailboard = db.relationship(
#         'User', secondary=staffs_on_tailboard,
#         primaryjoin=(staffs_on_tailboard.c.staff_on_tailboard_id == id),
#         secondaryjoin=(staffs_on_tailboard.c.staff_added_to_tailboard_id == id),
#         backref=db.backref('staffs_on_tailboard', lazy='dynamic'), lazy='dynamic')
# 
#     def add_vehicle(self, vehicle):
#         if not self.what_vehicles_are_on_tailboard(vehicle):
#             self.vehicle_added_to_tailboard.append(vehicle)
# 
#     def remove_vehicle(self, vehicle):
#         if self.what_vehicles_are_on_tailboard(vehicle):
#             self.vehicle_added_to_tailboard.remove(vehicle)
# 
#     def what_vehicles_are_on_tailboard(self, vehicle):
#         return self.vehicle_added_to_tailboard.filter(
#             vehicles_on_tailboard.c.vehicle_added_to_tailboard_id == vehicle.id).count() > 0
# 
#     def add_present_danger(self, present_danger):
#         if not self.what_present_dangers_are_on_tailboard(present_danger):
#             self.present_danger_added_to_tailboard.append(present_danger)
# 
#     def remove_present_danger(self, present_danger):
#         if self.what_present_dangers_are_on_tailboard(present_danger):
#             self.present_danger_added_to_tailboard.remove(present_danger)
# 
#     def what_present_dangers_are_on_tailboard(self, present_danger):
#         return self.present_danger_added_to_tailboard.filter(
#             present_dangers_on_tailboard.c.present_danger_added_to_tailboard_id == present_danger.id).count() > 0
# 
#     def add_controls_barrier(self, controls_barrier):
#         if not self.what_controls_barriers_are_on_tailboard(controls_barrier):
#             self.controls_barrier_added_to_tailboard.append(controls_barrier)
# 
#     def remove_controls_barrier(self, controls_barrier):
#         if self.what_controls_barriers_are_on_tailboard(controls_barrier):
#             self.controls_barrier_added_to_tailboard.remove(controls_barrier)
# 
#     def what_controls_barriers_are_on_tailboard(self, controls_barrier):
#         return self.controls_barrier_added_to_tailboard.filter(
#             controls_barriers_on_tailboard.c.controls_barrier_added_to_tailboard_id == controls_barrier.id).count() > 0
# 
#     def add_staff(self, user):
#         if not self.what_staffs_are_on_tailboard(user):
#             self.staff_added_to_tailboard.append(user)
# 
#     def remove_staff(self, user):
#         if self.what_staffs_are_on_tailboard(user):
#             self.staff_added_to_tailboard.remove(user)
# 
#     def what_staffs_are_on_tailboard(self, user):
#         return self.staff_added_to_tailboard.filter(
#             staffs_on_tailboard.c.staff_added_to_tailboard_id == user.id).count() > 0    
            
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
