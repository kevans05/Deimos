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
                           title='New Staff')
@app.route('/handleNewStaff', methods=['POST'])
def handleNewStaff():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['staff']
        table.insert(dict(firstName=request.form['inputFirstName'], lastName=request.form['inputLastName'], email=request.form['inputEmail'], tel=request.form['inputPhoneNumber'],enabled=1))

    return redirect('/')

@app.route('/removeStaff')
def removeStaff():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['staff']
    staff = table.find(enabled=1)
    return render_template('staffRemove.html',
                           title='New Staff',staff=staff)

@app.route('/handleRemoveStaff', methods=['POST'])
def handleRemoveStaff():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['staff']
        for x in request.form.getlist('removeStaff'):
            table.update(dict(id=x,enabled=0),['id'])
    return redirect('/')

@app.route('/editStaff')
def editStaff():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['staff']
    return render_template('staffEdit.html',
                           title='New Staff',staff=table)

@app.route('/handleEditStaff', methods=['POST'])
def handleEditStaff():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['staff']
        table.update(dict(id=request.form['inputid'], firstName=request.form['inputFirstName'],lastName=request.form['inputLastName'], email=request.form['inputEmail'],tel=request.form['inputPhoneNumber'],enabled=['activeStaff']), ['id'])
    return redirect('/')

@app.route('/newVehicle')
def newVehicle():
    return render_template('vehicleNew.html',
                           title='New Vehicle')
@app.route('/handleNewVehicle', methods=['POST'])
def handleNewVehicle():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['vehicle']
        print(request.form)
        table.insert(dict(nickname=request.form['inputNickname'],
                          corporationID=request.form['inputCorporationID'], make=request.form['inputMake'],
                          model=request.form['inputModel'],enabled=1))

    return redirect('/')

@app.route('/removeVehicle')
def removeVehicle():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['vehicle']
    vehicle = table.find(enabled=1)
    return render_template('vehicleRemove.html',
                           title='New Vehicle',vehicle=vehicle)

@app.route('/handleRemoveVehicle', methods=['POST'])
def handleRemoveVehicle():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['vehicle']
        for x in request.form.getlist('removeVehicle'):
            table.update(dict(id=x,enabled=0),['id'])
    return redirect('/')

@app.route('/editVehicle')
def editVehicle():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['vehicle']
    return render_template('vehicleEdit.html',
                           title='New Vehicle',vehicle=table)
@app.route('/handleEditVehicle', methods=['POST'])
def handleEditVehicle():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['vehicle']
        table.update(dict(nickname=request.form['inputNickname'],
                          corporationID=request.form['inputCorporationID'], make=request.form['inputMake'],
                          model=request.form['inputModel'],enabled=['activeVehicle']), ['id'])
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html',
                           title='about', page='about')