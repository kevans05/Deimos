from . import app
from flask import render_template, request

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')


@app.route('/about')
def about():
    return render_template('about.html',
                           title='about', page='about')