import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'evans.j.k05@gmail.com'
MAIL_PASSWORD = 'M3z6jjg3G9Rr3e7B'

# administrator list
ADMINS = ['your-gmail-username@gmail.com']