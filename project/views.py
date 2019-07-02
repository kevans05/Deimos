import json
import os
import dataset
import xlsxwriter
import atexit
from time import time, strftime, localtime
from datetime import datetime
from flask import render_template, request, redirect, flash, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from project import app
from .basicModules import parse_a_database_return_a_list, parse_a_database_return_a_list_users
from .email import newTailboardEmail, managers_email_initiate
from .token import confirm_token

path_d = ["project/dynamic/xlsx"]

@app.before_first_request
def activate_job():
    for path in path_d:
        try:
            os.makedirs(path)
            print(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s" % path)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')


@app.route('/newTailboard')
def newTailboard():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')

    return render_template('newTailboard.html', staff=db['staff'].find(enabled=1),
                           vehicle=db['vehicle'].find(enabled=1),presentDangers=db['presentDangers'].find(enabled=1),controlsBarriers=db['controlsBarriers'].find(enabled=1))


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
        newTailboardEmail(jobID)
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
                          tel=request.form['inputPhoneNumber'], supervisorEmail=request.form['supervisorEmail'],
                          enabled=True))
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
        data = dict(id=request.form['inputid'], firstName=request.form['inputFirstName'],
                    lastName=request.form['inputLastName'],
                    corporateID=request.form['inputCorpID'], email=request.form['inputEmail'],
                    tel=request.form['inputPhoneNumber'], supervisorEmail=request.form['supervisorEmail'],
                    enabled=request.form['activeStaff'])
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


@app.route('/reinstateVehicle')
def reinstateVehicle():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['vehicle']
    vehicle = table.find(enabled=False)
    return render_template('vehicleReinstate.html',
                           title='New Vehicle', vehicle=vehicle)


@app.route('/handleReinstateVehicle', methods=['POST'])
def handleReinstateVehicle():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['vehicle']
        for x in request.form.getlist('reinstateVehicle'):
            table.update(dict(id=x, enabled=True), ['id'])
    return redirect('/')


@app.route('/newPresentDangers')
def newPresentDangers():
    return render_template('presentDangersNew.html',
                           title='New Present Dangers')


@app.route('/handlNewPresentDangers', methods=['POST'])
def handlNewPresentDangers():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['presentDangers']
        table.insert(dict(danger=request.form['newPresentDanger'], enabled=True))
    return redirect('/')


@app.route('/removePresentDangers')
def removePresentDangers():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['presentDangers']
    presentDangers = table.find(enabled=True)
    return render_template('presentDangersRemove.html',
                           title='Present Danger', presentDangers=presentDangers)


@app.route('/handleRemovePresentDangers', methods=['POST'])
def handleRemovePresentDangers():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['presentDangers']
        for x in request.form.getlist('removePresentDangers'):
            table.update(dict(id=x, enabled=False), ['id'])
    return redirect('/')


@app.route('/reinstatePresentDangers')
def reinstatePresentDangers():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['presentDangers']
    presentDangers = table.find(enabled=False)
    return render_template('presentDangersReinstate.html',
                           title='Present Dangers', presentDangers=presentDangers)


@app.route('/handleReinstatePresentDanger', methods=['POST'])
def handleReinstatePresentDanger():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['presentDangers']
        for x in request.form.getlist('reinstatePresentDanger'):
            table.update(dict(id=x, enabled=True), ['id'])
    return redirect('/')


@app.route('/newControlsBarriers')
def newControlsBarriers():
    return render_template('controlsBarriersNew.html',
                           title='New Present Dangers')


@app.route('/handlNewControlsBarriers', methods=['POST'])
def handlNewControlsBarriers():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['controlsBarriers']
        table.insert(dict(controlsBarriers=request.form['newControlsBarriers'], enabled=True))
    return redirect('/')


@app.route('/removeControlsBarriers')
def removeControlsBarriers():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['controlsBarriers']
    controlsBarriers = table.find(enabled=True)
    return render_template('controlsBarriersRemove.html',
                           title='Remove Present Dangers', controlsBarriers=controlsBarriers)


@app.route('/handleRemoveControlsBarriers', methods=['POST'])
def handleRemoveControlsBarriers():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['controlsBarriers']
        for x in request.form.getlist('removeControlsBarriers'):
            table.update(dict(id=x, enabled=False), ['id'])
    return redirect('/')


@app.route('/reinstateControlsBarriers')
def reinstateControlsBarriers():
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    table = db['controlsBarriers']
    controlsBarriers = table.find(enabled=False)
    return render_template('controlsBarriersReinstate.html',
                           title='Present Dangers', controlsBarriers=controlsBarriers)


@app.route('/handleReinstateControlsBarriers', methods=['POST'])
def handleReinstateControlsBarriers():
    if request.method == 'POST':
        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        table = db['controlsBarriers']
        for x in request.form.getlist('reinstateControlsBarriers'):
            table.update(dict(id=x, enabled=True), ['id'])
    return redirect('/')


@app.route('/emailSettings')
def emailSettings():
    return render_template('emailSettings.html',
                           title='Edit Settings')


@app.route('/handleEmailSettings' , methods=['POST'])
def handleEmailSettings():
    if request.method == 'POST':
        admin = "['" + request.form['admin_email'] + "']"
        if request.form['mailUseTLS'] == "true":
            mail_uses_tls = True
        else:
            mail_uses_tls = False
        if request.form['mailUseSSL'] == "true":
            mail_uses_ssl = True
        else:
            mail_uses_ssl = False

        data = {'mailServer':request.form['mailServer'], 'mailPort':request.form['mailPort'],
                          'mailUseTLS':mail_uses_tls, 'mailUseSSL':mail_uses_ssl,
                          'username':request.form['username'], 'password':request.form['password'], 'admin':admin}
        with open('project/dynamic/db/email_server_settings.txt','w') as outfile:
            json.dump(data,outfile)
    return redirect('/')


@app.route('/adminSettings')
def adminSettings():
    return render_template('adminSettings.html',
                           title='Admin Settings')


@app.route('/reminderSettings')
def reminderSettings():
    return render_template('reminderSettings.html',
                           title='Admin Settings')

@app.route('/handleReminderSettings' , methods=['POST'])
def handleReminderSettings():
    if request.method == 'POST':
        data = {'mail_server_time': request.form['mailServerTime'], 'health_and_safety_email': request.form['healthAndSafetyEmail']}
        with open('project/dynamic/db/reminder_settings.txt', 'w') as outfile:
            json.dump(data, outfile)
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
        tailboardDict = {"jobID": user['jobID'], "jobDate": user['jobDate'], "location": user['location'],
                         "presentStaff": name}
        tailboard.append(tailboardDict)
    return render_template('archives.html',
                           title='archives', page='archives', tailboards=tailboard)


@app.route('/handleArchives/<tailboardID>')
def handleArchives(tailboardID):
    present_voltage_dictionary = {"ground": False, "lessThan": False, "greaterThen": False}
    #pull in the database at its current state
    db = dataset.connect('sqlite:///project/dynamic/db/database.db')
    #in the database find the the tailboard that matches the tailboard ID selected
    tailboard = db['tailboard'].find_one(jobID=tailboardID)
    if tailboard['presentVoltages'] is not None:
        for present_voltage in tailboard['presentVoltages'].split(';'):
            present_voltage_dictionary[present_voltage] = True
    return render_template('archiveOutput.html', tailboardData=tailboard,
                           presentUserData=parse_a_database_return_a_list_users(db,tailboard),
                           presentVehiclesData=parse_a_database_return_a_list('vehicle',db,tailboard),
                           presentDangerDic=parse_a_database_return_a_list('presentDangers', db, tailboard),
                           presentVoltageDic=present_voltage_dictionary,
                           controlsBarriersDic=parse_a_database_return_a_list('controlsBarriers', db, tailboard),
                           title=tailboardID, page=tailboardID)

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
    presentDangersData = db['presentDangers']
    controlsBarriersData = db['controlsBarriers']
    workbook = xlsxwriter.Workbook('project/' + fileNameCreatWorkbook)
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, 'Job ID')
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
        worksheet.write(row, 9, usersNameText)
        presentUsersNameText = ""
        if tailboards['presentStaffConfirmed'] is not None:
            presentStaffConfirmed = tailboards['presentStaffConfirmed'].split(";")
            for users in presentStaffConfirmed:
                if len(users) > 0:
                    x = userData.find_one(id=users)
                    presentUsersNameText = x['firstName'] + " " + x['lastName'] + ";" + presentUsersNameText
        worksheet.write(row, 10, presentUsersNameText)
        vehicleText = ""
        if tailboards['vehicle'] is not None:
            vehicleList = tailboards['vehicle'].split(";")
            for vehicle in vehicleList:
                x = vehicleData.find_one(id=vehicle)
                vehicleText = x['corporationID'] + ";" + vehicleText
        worksheet.write(row, 11, vehicleText)
        presentDangersText = ""
        if tailboards['presentDangers'] is not None:
            presentDangersList = tailboards['presentDangers'].split(";")
            for presentDangers in presentDangersList:
                x = presentDangersData.find_one(id=presentDangers)
                presentDangersText = x['danger'] + ";" + presentDangersText
        worksheet.write(row, 3, presentDangersText)
        controlsBarriersText = ""
        if tailboards['controlsBarriers'] is not None:
            controlsBarriersList = tailboards['controlsBarriers'].split(";")
            for controlsBarriers in controlsBarriersList:
                x = controlsBarriersData.find_one(id=controlsBarriers)
                controlsBarriersText = x['controlsBarriers'] + ";" + controlsBarriersText
        worksheet.write(row, 4, controlsBarriersText)
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


@app.before_first_request
def activate_job():
    managers_email_initiate()

