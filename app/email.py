from flask import render_template, url_for
from flask_mail import Message
from threading import Thread
from app import mail
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from collections import defaultdict

import dataset
import atexit
import json

from app import app
from app.models import User, Vehicle, Dangers, Barriers, Tailboard, Voltages, Tailboard_Users
from .token import generate_confirmation_token
from .basicModules import parse_a_database_return_a_list_users, parse_a_database_return_a_list


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

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

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


# Function: newTailboardEmail
# ----------------------------
#   INPUTS:
#       tailboardID: this is used by the software to look up the data needed for generating the
#           tailboard information in an email
#   RETURNS:
#       0
#   DESCRIPTION:
#       the software looks threw all the database, parses out all the complex data and preps it for an email.

def new_tailboard_email(tailboardID):
    tailboard = Tailboard.query.join(Tailboard_Users).join(User).filter((Tailboard_Users.tailboard_id == tailboardID) & (Tailboard_Users.sign_on_time == None)).first()
    users = User.query.join(Tailboard_Users).join(Tailboard).filter((Tailboard_Users.tailboard_id == tailboardID)).all()
    for x in users:
        print(x)
        send_email('[Deimos] Tailboard - ID:' + str(tailboard.id),
                   sender=app.config['ADMINS'][0],
                   recipients=[x.email],
                   text_body=render_template('email/archive_output_email.txt'),
                   html_body=render_template('email/archive_output_email.html', tailboard=tailboard,
                           presentUserData = Tailboard_Users.query.join(User).filter((Tailboard_Users.tailboard_id == tailboardID)).all(),
                           presentVehiclesData = Vehicle.query.filter(Vehicle.tailboard.any(id=tailboardID)).all(),
                           presentDangerDic = Dangers.query.filter(Dangers.tailboard.any(id=tailboardID)).all(),
                           controlsBarriersDic = Barriers.query.filter(Barriers.tailboard.any(id=tailboardID)).all(),
                           voltageDic = Voltages.query.filter(Voltages.tailboard.any(id=tailboardID)).all(),
                           timeStamp = datetime(year=1970,month=1,day=1,hour=0,minute=0,second=0,microsecond=0))
                   )


# Function: sendReportToManager
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       finds all the tailboards that have taken place in the last 24 hours, find all the suppervisors and generate an email
def send_report_to_manager():
    import flask
    dictionaryOfSupervisorsandAssosiatedTailboard = {}
    list_of_tailboards = []
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
        supervisor_email = key
        dictionary_of_tailboard = {}
        for tailboard in values:
            dictionary_of_tailboard = {'tailboard':tailboard,'users':parse_a_database_return_a_list_users(db, db['tailboard'].find_one(jobID=tailboard))}
            list_of_tailboards.append(dictionary_of_tailboard)
        print(supervisor_email)
        print(list_of_tailboards)
        x =  render_template('hello.html', name="bill")
        #sendEmail("Your team has been included on Tailboards from: %s - %s" % (twentyFourHoursAgo, datetime.now()),
                  #"evansk@londonhydro.com",[supervisor_email],"XX")





# Function: managersEmailInitiate
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       turns on timers for automatic emails
def managers_email_initiate():
    try:
        with open('project/dynamic/db/reminder_settings.txt') as json_file:
            data = json.load(json_file)
            x = datetime.strptime(data['mail_server_time'], '%H:%M').time()

            scheduler = BackgroundScheduler()
            scheduler.start()
            scheduler.add_job(
                func=send_report_to_manager,
                trigger=IntervalTrigger(seconds=5),
                #trigger=CronTrigger(hour=datetime.now().hour,minute=datetime.now().minute,second=(datetime.now().second+2)),
                id='printing_job',
                name='Print date and time every five seconds',
                replace_existing=True)
            # Shut down the scheduler when exiting the app
            atexit.register(lambda: scheduler.shutdown())
    except FileNotFoundError:
        return None

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Deimos] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))
