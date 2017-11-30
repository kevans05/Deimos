#################
#### imports ####
#################
from flask import Flask, render_template
################
#### config ####
################

app = Flask(__name__)
app.config.from_object('config')

from . import views