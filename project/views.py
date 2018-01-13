from time import time, strftime, localtime
from flask import render_template, request, redirect, flash, send_from_directory
from project import app
from .email import new_tailboard_email
from .token import confirm_token
import dataset
import xlsxwriter
import os

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')


@app.route('/newTailboard')
def newTailboard():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    return render_template('newTailboard.html', staff=db['staff'].find(enabled=1),
                           vehicle=db['vehicle'].find(enabled=1))


@app.route('/handleNewTailboard', methods=['POST'])
def handleNewTailboard():
    jobID = int(time())
    jobDate = strftime('%Y-%m-%d', localtime(jobID))
    if request.method == 'POST':
        tailboard = request.form.to_dict(flat=False)
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['tailboard']
        tailboardDict = {'jobID': jobID, 'jobDate': jobDate, 'presentStaffConfirmed': None}
        for key, values in tailboard.items():
            x = ';'.join(values)
            tailboardDict.update({key: x})
        table.insert(tailboardDict)
        new_tailboard_email(jobID)
    return redirect('/')


@app.route('/handleTailboardEmail/<token>')
def handleTailboardEmail(token):
    try:
        tokenInfo = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    tailboardData = db['tailboard']
    tailboard = tailboardData.find_one(jobID=tokenInfo[1])
    print(tailboard['presentStaffConfirmed'])
    if tailboard['presentStaffConfirmed'] is None:
        presentStaffConfirmed = str(tokenInfo[0]) + ";"
    else:
        presentStaffConfirmed = str(tailboard['presentStaffConfirmed']) + str(tokenInfo[0]) + ";"
    data = dict(jobID=tokenInfo[1], presentStaffConfirmed=presentStaffConfirmed)
    tailboardData.update(data, ['jobID'])
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
        table.insert(dict(firstName=request.form['inputFirstName'], lastName=request.form['inputLastName'],
                          corporateID=request.form['inputCorpID'], email=request.form['inputEmail'],
                          tel=request.form['inputPhoneNumber'], enabled=True))
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
            table.update(dict(id=x, enabled=False), ['id'])
    return redirect('/')


@app.route('/editStaff')
def editStaff():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['staff']
    return render_template('staffEdit.html',
                           title='New Staff', staff=table)


@app.route('/handleEditStaff', methods=['POST'])
def handleEditStaff():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['staff']
        data = dict(id=request.form['inputid'], firstName=request.form['inputFirstName'], lastName=request.form['inputLastName'],
                          corporateID=request.form['inputCorpID'], email=request.form['inputEmail'],
                          tel=request.form['inputPhoneNumber'], enabled=request.form['activeStaff'])
        print(data)
        table.update(data, ['id'])
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
                          model=request.form['inputModel'], enabled=True))
    return redirect('/')


@app.route('/removeVehicle')
def removeVehicle():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['vehicle']
    vehicle = table.find(enabled=True)
    return render_template('vehicleRemove.html',
                           title='New Vehicle', vehicle=vehicle)


@app.route('/handleRemoveVehicle', methods=['POST'])
def handleRemoveVehicle():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['vehicle']
        for x in request.form.getlist('removeVehicle'):
            table.update(dict(id=x, enabled=False), ['id'])
    return redirect('/')


@app.route('/editVehicle')
def editVehicle():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['vehicle']
    return render_template('vehicleEdit.html',
                           title='New Vehicle', vehicle=table)


@app.route('/handleEditVehicle', methods=['POST'])
def handleEditVehicle():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['vehicle']
        data = dict(id=request.form['inputid'], nickname=request.form['inputNickname'],
                    corporationID=request.form['inputCorporationID'], make=request.form['inputMake'],
                    model=request.form['inputModel'], enabled=request.form['inputActive'])
        table.update(data, ['id'])
    return redirect('/')


@app.route('/archives')
def archives():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    tailboardsTable = db['tailboard']
    userData = db['staff']
    tailboard = []

    for user in tailboardsTable:
        if user["presentStaff"] is not None:
            if ';' in user["presentStaff"]:
                users = user["presentStaff"].split(";")
            else:
                users = user["presentStaff"]
            name = ""
            for fullNames in users:
                x = userData.find_one(id=fullNames)
                fullName = (x['firstName'] + " " + x['lastName'] + ";")
                name = name + fullName
        tailboardDict = {"jobID":user['jobID'], "jobDate":user['jobDate'], "location":user['location'],"presentStaff":name}
        tailboard.append(tailboardDict)
    return render_template('archives.html',
                           title='archives', page='archives', tailboards=tailboard)


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
    if tailboardData['presentStaff'] is not None:
        presentUsers = tailboardData['presentStaff'].split(";")
    if tailboardData['presentVehicles'] is not None:
        presentVehicles = tailboardData['presentVehicles'].split(";")
    if tailboardData['presentStaffConfirmed'] is not None:
        presnetUsersConfirmed = tailboardData['presentStaffConfirmed'].split(";")
    else:
        presnetUsersConfirmed = []

    cuttingValueA = (len(presentUsers) + len(presentVehicles))

    userData = db['staff']

    for users in presentUsers:
        x = userData.find_one(id=users)
        if users in presnetUsersConfirmed:
            x.update({'present': True})
        presentUserData.append(x)

    vehicleData = db['vehicle']
    for vehicle in presentVehicles:
        presentVehicleData.append(vehicleData.find_one(id=vehicle))
    if tailboardData['presentDangers'] is not None:
        for presentDangers in tailboardData['presentDangers'].split(';'):
            presentDangerDic[presentDangers] = True
    if tailboardData['presentVoltages'] is not None:
        for presentVoltages in tailboardData['presentVoltages'].split(';'):
            presentVoltageDic[presentVoltages] = True
    if tailboardData['ControlsBarriers'] is not None:
        for controlsBarriers in tailboardData['ControlsBarriers'].split(';'):
            controlsBarriersDic[controlsBarriers] = True
    return render_template('archiveOutput.html', tailboardData=tailboardData, presentUserData=presentUserData,
                           presentVehiclesData=presentVehicleData, cuttingValueA=cuttingValueA,
                           presentDangerDic=presentDangerDic, presentVoltageDic=presentVoltageDic,
                           controlsBarriersDic=controlsBarriersDic, title=tailboardID, page=tailboardID)


@app.route('/about')
def about():
    return render_template('about.html',
                           title='about', page='about')

@app.route('/exportDataBase.xlsx')
def exportDataBase():
    filename = str(int(time())) + 'databaseExport.xlsx'
    fileLocation = 'dynamic/xlsx/'
    fileNameCreatWorkbook = fileLocation + filename
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    tailboardsTable = db['tailboard']
    userData = db['staff']
    vehicleData = db['vehicle']

    workbook = xlsxwriter.Workbook('project/' + fileNameCreatWorkbook)
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0,'Job ID')
    worksheet.write(0, 1, 'Date')
    worksheet.write(0, 2, 'Voltages')
    worksheet.write(0, 3, 'Present Dangers')
    worksheet.write(0, 4, 'Controls Barriers')
    worksheet.write(0, 5, 'Location')
    worksheet.write(0, 6, 'Job Steps')
    worksheet.write(0, 7, 'Hazards')
    worksheet.write(0, 8, 'Barrriers Mitigation')
    worksheet.write(0, 9, 'Present Staff')
    worksheet.write(0, 10, 'Present Staff Confirmed')
    worksheet.write(0, 11, 'present Vehicles')

    row = 1

    for tailboards in tailboardsTable:
        worksheet.write(row, 0, tailboards['jobID'])
        worksheet.write(row, 1, tailboards['jobDate'])
        worksheet.write(row, 2, tailboards['presentVoltages'])
        worksheet.write(row, 3, tailboards['presentDangers'])
        worksheet.write(row, 4, tailboards['ControlsBarriers'])
        worksheet.write(row, 5, tailboards['location'])
        worksheet.write(row, 6, tailboards['jobSteps'])
        worksheet.write(row, 7, tailboards['hazards'])
        worksheet.write(row, 8, tailboards['barrriersMitigation'])

        usersNameText = ""
        if tailboards['presentStaff'] is not None:
            presentUsersList = tailboards['presentStaff'].split(";")
            for users in presentUsersList:
                x = userData.find_one(id=users)
                usersNameText = x['firstName'] + " " + x['lastName'] + ";" + usersNameText
        worksheet.write(row,9,usersNameText)

        presentUsersNameText = ""
        if tailboards['presentStaffConfirmed'] is not None:
            presentStaffConfirmed = tailboards['presentStaffConfirmed'].split(";")
            for users in presentStaffConfirmed:
                if len(users) > 0:
                    x = userData.find_one(id=users)
                    presentUsersNameText = x['firstName'] + " " + x['lastName'] + ";" + presentUsersNameText
        worksheet.write(row,10,presentUsersNameText)

        vehicleText = ""
        if tailboards['presentVehicles'] is not None:
            vehicleList = tailboards['presentVehicles'].split(";")
            for vehicle in vehicleList:
                x = vehicleData.find_one(id=vehicle)
                vehicleText = x['corporationID'] + ";" + vehicleText
        worksheet.write(row, 11, vehicleText)

        row += 1

    workbook.close()
    return send_from_directory(fileLocation, filename)

@app.after_request
def per_request_callbacks(response):
    mydir = 'project/dynamic/xlsx/'
    if os.listdir(mydir) == "":
        return 0
    else:
        filelist = [f for f in os.listdir(mydir) if f.endswith(".xlsx")]
        for f in filelist:
            os.remove(os.path.join(mydir, f))
    return response