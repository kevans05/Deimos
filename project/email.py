from flask import render_template, url_for
from flask_mail import Message
from project import mail
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from collections import defaultdict

import dataset
import atexit

from .token import generate_confirmation_token

# Function: sendEmail
# ----------------------------
#   INPUTS:
#       subject: this is the subject line of the email to be sent
#       sender: the email that it will appear to be sent from
#       recipients: the email address that the email will be sent to
#       html_body: the html template that will be used to send the tailboard data -
#           I am only using html at the moment, I know I should have a text version but that's a long term goal
#   RETURNS:
#       0
#   DESCRIPTION:
#       this function uses the flask mail functions to send an email - currently it is only being used by the new_
#       tailboard_email function but will be used when the managers get a daily summery

def sendEmail(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)

# Function: newTailboardEmail
# ----------------------------
#   INPUTS:
#       tailboardID: this is used by the software to look up the data needed for generating the
#           tailboard information in an email
#   RETURNS:
#       0
#   DESCRIPTION:
#       the software looks threw all the database, parses out all the complex data and preps it for an email.

def newTailboardEmail(tailboardID):
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


    userData = db['staff']
    for users in presentUsers:
        presentUserData.append(userData.find_one(id=users))

    vehicleData = db['vehicle']
    for vehicle in presentVehicles:
        presentVehicleData.append(vehicleData.find_one(id=vehicle))
    if tailboardData['presentDangers'] is not None:
        for presentDangers in tailboardData['presentDangers'].split(';'):
            presentDangerDic[presentDangers] = True
    if tailboardData['presentDangers'] is not None:
        for presentVoltages in tailboardData['presentVoltages'].split(';'):
            presentVoltageDic[presentVoltages] = True
    if tailboardData['ControlsBarriers'] is not None:
        for controlsBarriers in tailboardData['ControlsBarriers'].split(';'):
            controlsBarriersDic[controlsBarriers] = True
    for users in presentUserData:
        #tokenID = str(users['id']) str(tailboardID)
        token = generate_confirmation_token([users['id'],tailboardID])
        confirm_url = url_for('handleTailboardEmail', token=token, _external=True)
        sendEmail("You have been included in Tailboard: %s - %s" % (tailboardID, str(tailboardData['location'])), "evansk@londonhydro.com",
                  [users['email']], render_template('archiveOutputEmail.html', tailboardData=tailboardData,
                                                           presentUserData=presentUserData,
                                                           presentVehiclesData=presentVehicleData,
                                                           presentDangerDic=presentDangerDic,
                                                           presentVoltageDic=presentVoltageDic,
                                                           controlsBarriersDic=controlsBarriersDic, title=tailboardID,
                                                           firstName=users['firstName'],lastName=users['lastName'],token=confirm_url,
                                                           page=tailboardID))

# Function: sendReportToManager
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       finds all the tailboards that have taken place in the last 24 hours, find all the suppervisors and generate an email
def sendReportToManager():
        dictionaryOfSupervisorsandAssosiatedTailboard = defaultdict()

        db = dataset.connect('sqlite:///project/dynamic/db/database.db')
        twentyFourHoursAgo = datetime.now() - timedelta(days=1)

        allReportsFromLastTwentyFourHours = db['tailboard'].find(db['tailboard'].table.columns.jobDate > twentyFourHoursAgo)
        for currentTailboard in allReportsFromLastTwentyFourHours:
            for users in currentTailboard['presentStaff']:
                if users is not ';':
                    x = (db['staff'].find_one(id=users))
                    if x['supervisorEmail'] in dictionaryOfSupervisorsandAssosiatedTailboard.keys():
                         y = dictionaryOfSupervisorsandAssosiatedTailboard[x['supervisorEmail']]
                         y.append(currentTailboard['jobID'])
                         dictionaryOfSupervisorsandAssosiatedTailboard[x['supervisorEmail']] = y
                    else:
                        dictionaryOfSupervisorsandAssosiatedTailboard[x['supervisorEmail']] = [currentTailboard['jobID']]
        for key, values in dictionaryOfSupervisorsandAssosiatedTailboard.items():
            print(key, " : ", values)


# Function: managersEmailInitiate
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       turns on timers for automatic emails
def managersEmailInitiate():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=sendReportToManager,
        trigger=CronTrigger(hour=19,minute=5),
        id='printing_job',
        name='Print date and time every five seconds',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())



