from . import app
from flask import render_template, request, redirect, make_response
from time import time, strftime, localtime

import dataset


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@app.route('/newTailboard')
def newTailboard():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    return render_template('newTailboard.html', staff=db['staff'].find(enabled=1),vehicle=db['vehicle'].find(enabled=1))

@app.route('/handleNewTailboard', methods=['POST'])
def handleNewTailboard():
    jobID = int(time())
    jobDate = strftime('%Y-%m-%d', localtime(jobID))
    if request.method == 'POST':
        tailboard = request.form.to_dict(flat=False)
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['tailboard']
        tailboardDict = {'jobID':jobID, 'jobDate':jobDate}
        for key, values in tailboard.items():
            x = ';'.join(values)
            tailboardDict.update({key:x})
        table.insert(tailboardDict)
    return redirect('/')

@app.route('/newStaff')
def newStaff():
    return render_template('staffNew.html',
                           title='New Staff')
@app.route('/handleNewStaff', methods=['POST'])
def handleNewStaff():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['staff']
        table.insert(dict(firstName=request.form['inputFirstName'], lastName=request.form['inputLastName'], email=request.form['inputEmail'], tel=request.form['inputPhoneNumber'],enabled=True))
    return redirect('/')

@app.route('/removeStaff')
def removeStaff():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['staff']
    staff = table.find(enabled=True)
    return render_template('staffRemove.html',
                           title='New Staff', staff=staff)

@app.route('/handleRemoveStaff', methods=['POST'])
def handleRemoveStaff():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['staff']
        for x in request.form.getlist('removeStaff'):
            table.update(dict(id=x,enabled=False),['id'])
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
        table.update(dict(id=request.form['inputid'], firstName=request.form['inputFirstName'],lastName=request.form['inputLastName'], email=request.form['inputEmail'],tel=request.form['inputPhoneNumber'],enabled=['activeStaff']), request.form['inputid'])
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
        table.insert(dict(nickname=request.form['inputNickname'],
                          corporationID=request.form['inputCorporationID'], make=request.form['inputMake'],
                          model=request.form['inputModel'],enabled=True))
    return redirect('/')

@app.route('/removeVehicle')
def removeVehicle():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['vehicle']
    vehicle = table.find(enabled=True)
    return render_template('vehicleRemove.html',
                           title='New Vehicle',vehicle=vehicle)

@app.route('/handleRemoveVehicle', methods=['POST'])
def handleRemoveVehicle():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['vehicle']
        for x in request.form.getlist('removeVehicle'):
            table.update(dict(id=x,enabled=False),['id'])
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

@app.route('/archives')
def archives():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    tailboardsTable = db['tailboard']
    usersTable = db['Staff']

    return render_template('archives.html',
                           title='archives', page='archives', tailboards=tailboardsTable, users=usersTable)

@app.route('/handleArchives/<tailboardID>')
def handleArchives(tailboardID):
    presentVoltageDic = {"ground": False, "lessThan": False, "greaterThen": False}

    presentDangerDic = {"coldMeter": False, "hotMeter": False, "txRated": False, "testing": False, "siteVisits": False,
                        "nonTypical": False, "heights": False, "weatherStresses": False, "climbingHazards": False,
                        "confinedSpace": False}

    controlsBarriersDic = {"rubberGloves": False, "fallProtection": False, "rescuePlan": False,
                           "PPE": False, "equipmentInspection": False, "trafficPlan": False}

    presentUserData = []
    presentVehicleData = []

    db = dataset.connect('sqlite:///project/dynamic/db/database.db')

    tailboardData = db['tailboard'].find_one(jobID=tailboardID)
    presentUsers = tailboardData['presentStaff'].split(";")
    presentVehicles = tailboardData['presentVehicles'].split(";")

    cuttingValueA = (len(presentUsers) + len(presentVehicles))

    userData = db['staff']
    for users in presentUsers:
        presentUserData.append(userData.find_one(id=users))

    vehicleData = db['vehicle']
    for vehicle in presentVehicles:
        presentVehicleData.append(vehicleData.find_one(id=vehicle))

    for presentDangers in tailboardData['presentDangers'].split(';'):
        presentDangerDic[presentDangers] = True

    for presentVoltages in tailboardData['presentVoltages'].split(';'):
        presentVoltageDic[presentVoltages] = True

    for controlsBarriers in tailboardData['ControlsBarriers'].split(';'):
        controlsBarriersDic[controlsBarriers] = True

    return render_template('archiveOutput.html', tailboardData=tailboardData, presentUserData=presentUserData,
                           presentVehiclesData=presentVehicleData, cuttingValueA=cuttingValueA,
                           presentDangerDic=presentDangerDic,presentVoltageDic=presentVoltageDic,
                           controlsBarriersDic=controlsBarriersDic,title=tailboardID, page=tailboardID)
@app.route('/about')
def about():
    return render_template('about.html',
                           title='about', page='about')

