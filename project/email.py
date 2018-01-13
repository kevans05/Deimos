from flask import render_template, url_for
from flask_mail import Message
from project import mail
from .token import generate_confirmation_token
import dataset


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)


def new_tailboard_email(tailboardID):
    presentVoltageDic = {"ground": False, "lessThan": False, "greaterThen": False}

    presentDangerDic = {"coldMeter": False, "hotMeter": False, "txRated": False, "testing": False, "siteVisits": False,
                        "nonTypical": False, "heights": False, "weatherStresses": False, "climbingHazards": False,
                        "confinedSpace": False}

    controlsBarriersDic = {"rubberGloves": False, "fallProtection": False, "rescuePlan": False,
                           "PPE": False, "equipmentInspection": False, "trafficPlan": False}

    presentUserData = []
    presentVehicleData = []
    presentEmails = []

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
        send_email("You have been included in Tailboard: %s - %s" % (tailboardID, str(tailboardData['location'])), "evansk@londonhydro.com",
                   [users['email']], render_template('archiveOutputEmail.html', tailboardData=tailboardData,
                                                           presentUserData=presentUserData,
                                                           presentVehiclesData=presentVehicleData,
                                                           presentDangerDic=presentDangerDic,
                                                           presentVoltageDic=presentVoltageDic,
                                                           controlsBarriersDic=controlsBarriersDic, title=tailboardID,
                                                           firstName=users['firstName'],lastName=users['lastName'],token=confirm_url,
                                                           page=tailboardID))
