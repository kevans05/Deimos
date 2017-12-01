from . import app
from flask import render_template, request, redirect

import dataset

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')
@app.route('/newStaff')
def newStaff():
    return render_template('staffNew.html',
                           title='about', page='about')

@app.route('/handleNewStaff', methods=['POST'])
def handleNewStaff():
    db = dataset.connect('sqlite:///mydatabase.db')
    table = db['CDMUsers']
    table.insert(dict(firstName="xx"))
    if request.method == 'POST':
        print(request.form['inputFirstName'])
       #'table.insert(dict(firstName=request.form['inputFirstName'], lastName=request.form['inputLastName'], email=request.form['inputEmail'], tel=request.form['inputPhoneNumber']))
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html',
                           title='about', page='about')