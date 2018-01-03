#################
#### imports ####
#################
from flask import Flask
from flask_mail import Mail

################
#### config ####
################

app = Flask(__name__)
mail = Mail(app)
app.config.from_object('config')


from . import views