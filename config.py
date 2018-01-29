import os
import json
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SECURITY_PASSWORD_SALT = 'my_precious_two'
try:
    with open('project/dynamic/db/email_server_settings.txt') as json_file:
            data = json.load(json_file)
            MAIL_SERVER = data['mailServer']
            MAIL_PORT = data['mailPort']
            MAIL_USE_TLS = data['mailUseTLS']
            MAIL_USE_SSL = data['mailUseSSL']
            MAIL_USERNAME = data['username']
            MAIL_PASSWORD = data['password']
            ADMINS = data['admin']
except FileNotFoundError:
    # email server
    MAIL_SERVER = 'smtp.somefakeserver.ca'
    MAIL_PORT = 666
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'evans.j.k05@somefakeserver.ca'
    MAIL_PASSWORD = 'my_precious_two'
    # administrator list
    ADMINS = ['evansk@londonhydro.com']

# email server
#MAIL_SERVER = 'smtp.googlemail.com'
#MAIL_PORT = 465
#MAIL_USE_TLS = False
#MAIL_USE_SSL = True
#MAIL_USERNAME = 'evans.j.k05@gmail.com'
#MAIL_PASSWORD = 'M3z6jjg3G9Rr3e7B'


# administrator list
#ADMINS = ['evansk@londonhydro.com']
