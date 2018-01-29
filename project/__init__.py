#################
#### imports ####
#################
from flask import Flask
from flask_mail import Mail




###############
#### config ####
################

from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL,\
 MAIL_USERNAME, MAIL_PASSWORD, ADMINS

app = Flask(__name__)
app.config.from_object('config')


mail = Mail(app)
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler

    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT),
                               'no-reply@' + MAIL_SERVER, ADMINS,
                               'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

from project import views