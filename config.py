import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'evans.j.k05@gmail.com'
    MAIL_PASSWORD = 'hszlnafnuutobjin'
    ADMINS = ['your-email@example.com']
        
