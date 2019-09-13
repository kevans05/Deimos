from project import db
from project import login

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64),index=True,unique=True)
    lastName = db.Column(db.String(64),index=True,unique=True)
    corporateID = db.Column(db.Integer,index=True,unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    tel = db.Column(db.String(120), index=True, unique=True)
    supervisorEmail = db.Column(db.String(120), index=True, unique=True)
    enabled = db.Column(db.Boolean, index=True,unique=True)
    password_hash = db.Column(db.String(128))


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


