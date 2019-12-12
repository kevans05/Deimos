import json
import os
import csv
from time import time
from datetime import datetime
from flask import render_template, request, redirect, flash, send_from_directory, url_for
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.models import User, Vehicle, Dangers, Barriers, Tailboard, Voltages, Tailboard_Users
from .token import confirm_token
from app.email import send_password_reset_email, new_tailboard_email, sign_off_email

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

####################################################################################################################################
#-----------------------------------------------------index and in app signing-----------------------------------------------------#

# Function: index
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        myTailboards = Tailboard.query.join(Tailboard_Users).join(User).filter(
            (Tailboard_Users.user_id == current_user.id) & (Tailboard_Users.sign_on_time == None)).all()

        workingTailboards = Tailboard.query.join(Tailboard_Users).join(User).filter(
            (Tailboard_Users.user_id == current_user.id) & (
                        Tailboard_Users.sign_on_time > datetime(year=1971, month=1, day=1, hour=0, minute=0, second=0,
                                                                microsecond=0)) & (
                        Tailboard_Users.sign_off_time == None)).all()

        return render_template('index.html',
                               title='Current Tailboards', myTailboards=myTailboards,
                               workingTailboards=workingTailboards)
    else:
        return render_template('index.html',
                               title='Home')

# Function: signOffTailboard
# ----------------------------
#   INPUTS:
#       tailboardID
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/signOffTailboard/<tailboardID>')
def signOffTailboard(tailboardID):
    tailboardToJoin = Tailboard_Users.query.filter(
        (Tailboard_Users.user_id == current_user.id) & (Tailboard_Users.tailboard_id == tailboardID)).first()
    if tailboardToJoin.sign_off_time is not None:
        tailboardToJoin.sign_off_time = datetime.utcnow()
        db.session.commit()
    return redirect('/')

# Function: joinTailboard
# ----------------------------
#   INPUTS:
#       tailboardID
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/joinTailboard/<tailboardID>')
def joinTailboard(tailboardID):
    tailboardToJoin = Tailboard_Users.query.filter(
        (Tailboard_Users.user_id == current_user.id) & (Tailboard_Users.tailboard_id == tailboardID)).first()
    tailboardToJoin.sign_on_time = datetime.utcnow()
    db.session.commit()
    sign_off_email(tailboardToJoin)
    return redirect('/')

# Function: refuseTailboard
# ----------------------------
#   INPUTS:
#       tailboardID
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/refuseTailboard/<tailboardID>')
def refuseTailboard(tailboardID):
    tailboardToJoin = Tailboard_Users.query.filter(
        (Tailboard_Users.user_id == current_user.id) & (Tailboard_Users.tailboard_id == tailboardID)).first()
    tailboardToJoin.sign_on_time = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    db.session.commit()
    return redirect('/')

####################################################################################################################################
#------------------------------------------------------------tailboard-------------------------------------------------------------#

# Function: newTailboard
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/newTailboard', methods=['GET', 'POST'])
@login_required
def newTailboard():
    controlBarriers = Barriers.query.all()
    presentDangers = Dangers.query.all()
    vehicle = Vehicle.query.all()
    user = User.query.all()
    voltages = Voltages.query.all()
    if request.method == 'POST':

        tailboard = Tailboard(timestamp=datetime.utcnow(), location=request.form['location'],
                              jobSteps=request.form['jobSteps'], jobHazards=request.form['hazards'],
                              jobProtectios=request.form['barrriersMitigation'])

        for i in request.form.getlist("vehicle"):
            vehicle_to_add = Vehicle.query.get(i)
            tailboard.add_vehicle(vehicle_to_add)
        for i in request.form.getlist("presentStaff"):
            user_to_add = User.query.get(i)
            tailboard.add_user(user_to_add)
        for i in request.form.getlist("presentDangers"):
            present_dangers_to_add = Dangers.query.get(i)
            tailboard.add_danger(present_dangers_to_add)
        for i in request.form.getlist("controlsBarriers"):
            controls_barriers_to_add = Barriers.query.get(i)
            tailboard.add_barriers(controls_barriers_to_add)
        for i in request.form.getlist("voltage"):
            voltage_to_add = Voltages.query.get(i)
            tailboard.add_voltage(voltage_to_add)
        db.session.add(tailboard)
        db.session.commit()
        new_tailboard_email(tailboard.id)
        return redirect('/')
    return render_template('newTailboard.html', staff=user,
                           vehicle=vehicle, presentDangers=presentDangers, controlsBarriers=controlBarriers,
                           voltage=voltages)

####################################################################################################################################
#-------------------------------------------------------------vehicle--------------------------------------------------------------#

# Function: newVehicle
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/newVehicle', methods=['GET', 'POST'])
def newVehicle():
    if request.method == 'POST':
        vehicle = Vehicle(nickname=request.form['inputNickname'],
                          corporationID=request.form['inputCorporationID'], make=request.form['inputMake'],
                          model=request.form['inputModel'], enabled=True)
        db.session.add(vehicle)
        db.session.commit()
        return redirect('newVehicle')
    return render_template('vehicleNew.html',
                           title='New Vehicle')

# Function: editVehicle
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/editVehicle', methods=['GET', 'POST'])
def editVehicle():
    vehicle = Vehicle.query.all()
    if request.method == 'POST':
        target_vehicle = Vehicle.query.filter_by(id=request.form['inputid']).first()
        target_vehicle.nickname = request.form['inputNickname']
        target_vehicle.corporationID = request.form['inputCorporationID']
        target_vehicle.make = request.form['inputMake']
        target_vehicle.model = request.form['inputModel']
        db.session.commit()
        return redirect('/')
    return render_template('vehicleEdit.html',
                           title='Edit Vehicle', vehicle=vehicle)

####################################################################################################################################
#----------------------------------------------------------PresentDangers----------------------------------------------------------#

# Function: newPresentDangers
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/newPresentDangers', methods=['GET', 'POST'])
def newPresentDangers():
    if request.method == 'POST':
        presentDangers = Dangers(dangers=request.form['newPresentDanger'], enabled=True)
        db.session.add(presentDangers)
        db.session.commit()
        return redirect('/')
    return render_template('presentDangersNew.html',
                           title='New Present Dangers')

# Function: editPresentDangers
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/editPresentDangers', methods=['GET', 'POST'])
def editPresentDangers():
    presentDangers = Dangers.query.all()
    if request.method == 'POST':
        target_presentDangers = Dangers.query.filter_by(id=request.form['inputid']).first()
        target_presentDangers.dangers = request.form['inputDangers']
        db.session.commit()
        return redirect('/')
    return render_template('presentDangersEdit.html',
                           title='Present Danger', presentDangers=presentDangers)

####################################################################################################################################
#----------------------------------------------------------ControlBarriers---------------------------------------------------------#

# Function: newControlBarriers
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/newControlBarriers', methods=['GET', 'POST'])
def newControlBarriers():
    if request.method == 'POST':
        barrier = Barriers(controlBarriers=request.form['newControlBarriers'], enabled=True)
        db.session.add(barrier)
        db.session.commit()
        return redirect('/')
    return render_template('controlsBarriersNew.html',
                           title='New Present Dangers')

# Function: editControlBarriers
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/editControlBarriers', methods=['GET', 'POST'])
def editControlBarriers():
    controlBarriers = Barriers.query.all()
    if request.method == 'POST':
        target_control_barrier = Barriers.query.filter_by(id=request.form['inputid']).first()
        target_control_barrier.controlBarriers = request.form['controlOrBarriers']
        db.session.commit()
        return redirect('/')
    return render_template('controlsBarriersEdit.html',
                           title='Present Danger', controlBarriers=controlBarriers)

####################################################################################################################################
#--------------------------------------------------------------Voltages------------------------------------------------------------#

# Function: newVoltages
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/newVoltages', methods=['GET', 'POST'])
def newVoltages():
    if request.method == 'POST':
        voltages = Voltages(voltage=request.form['newVoltage'], numberOfWires=request.form['numberOfWires'],
                            numberOfPhases=request.form['numberOfPhases'], enabled=True)
        db.session.add(voltages)
        db.session.commit()
        return redirect('/')
    return render_template('voltageNew.html',
                           title='New Voltage')

# Function: editVoltages
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/editVoltages', methods=['GET', 'POST'])
def editVoltages():
    voltages = Voltages.query.all()
    if request.method == 'POST':
        target_voltages = Voltages.query.filter_by(id=request.form['inputid']).first()
        target_voltages.voltages = request.form['voltages']
        target_voltages.numberOfWires = request.form['numberOfWires']
        target_voltages.numberOfPhases = request.form['numberOfPhases']
        db.session.commit()
        return redirect('/')
    return render_template('voltageEdit.html',
                           title='Voltages', voltage=voltages)


####################################################################################################################################
#------------------------------------------------------------email settings--------------------------------------------------------#

# Function: emailSettings
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/emailSettings')
def emailSettings():
    return render_template('emailSettings.html',
                           title='Edit Settings')

# Function: handleEmailSettings
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       to be merged into emailSettings
@app.route('/handleEmailSettings', methods=['POST'])
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

        data = {'mailServer': request.form['mailServer'], 'mailPort': request.form['mailPort'],
                'mailUseTLS': mail_uses_tls, 'mailUseSSL': mail_uses_ssl,
                'username': request.form['username'], 'password': request.form['password'], 'admin': admin}
        with open('project/dynamic/db/email_server_settings.txt', 'w') as outfile:
            json.dump(data, outfile)
    return redirect('/')

# Function: adminSettings
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/adminSettings')
def adminSettings():
    return render_template('adminSettings.html',
                           title='Admin Settings')

# Function: reminderSettings
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/reminderSettings')
def reminderSettings():
    return render_template('reminderSettings.html',
                           title='Admin Settings')

# Function: handleReminderSettings
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       to be merged into reminderSettings
@app.route('/handleReminderSettings', methods=['POST'])
def handleReminderSettings():
    if request.method == 'POST':
        data = {'mail_server_time': request.form['mailServerTime'],
                'health_and_safety_email': request.form['healthAndSafetyEmail']}
        with open('project/dynamic/db/reminder_settings.txt', 'w') as outfile:
            json.dump(data, outfile)
    return redirect('/')

####################################################################################################################################
#---------------------------------------------------------------archives-----------------------------------------------------------#

# Function: archives
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/archives')
def archives():
    tailboards = Tailboard.query.all()

    return render_template('archives.html',
                           title='archives', page='archives', tailboards=tailboards)

# Function: archives
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/handleArchives/<tailboardID>')
def handleArchives(tailboardID):
    tailboard_current = Tailboard.query.filter_by(id=tailboardID).first()

    return render_template('archiveOutput.html', tailboard=tailboard_current,
                           presentUserData=Tailboard_Users.query.join(User).filter(
                               (Tailboard_Users.tailboard_id == tailboardID)).all(),
                           presentVehiclesData=Vehicle.query.filter(Vehicle.tailboard.any(id=tailboardID)).all(),
                           presentDangerDic=Dangers.query.filter(Dangers.tailboard.any(id=tailboardID)).all(),
                           controlsBarriersDic=Barriers.query.filter(Barriers.tailboard.any(id=tailboardID)).all(),
                           voltageDic=Voltages.query.filter(Voltages.tailboard.any(id=tailboardID)).all(),
                           timeStamp=datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0))


####################################################################################################################################
#-----------------------------------------------------------------about------------------------------------------------------------#

# Function: about
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/about')
def about():
    return render_template('about.html',
                           title='about', page='about')

####################################################################################################################################
#---------------------------------------------------------------passwords----------------------------------------------------------#

# Function: reset_password_request
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['inputEmail']).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password')

# Function: reset_password
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user.set_password(request.form['password'])
        db.session.commit()
        print('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

# Function: login
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['inputEmail']).first()
        if user is None or not user.check_password(request.form['inputPassword']):
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In')

# Function: register
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User(firstName=request.form['inputFirstName'], lastName=request.form['inputLastName'],
                    corporateID=request.form['inputCorpID'], email=request.form['inputEmail'],
                    tel=request.form['inputPhoneNumber'], supervisorEmail=request.form['supervisorEmail'],
                    enabled=True)
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('login')
    return render_template('register.html', title='Register')

# Function: logout
# ----------------------------
#   INPUTS:
#       0
#   RETURNS:
#       0
#   DESCRIPTION:
#       0
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

####################################################################################################################################
#--------------------------------------------------------------EMAILS--------------------------------------------------------------#

@app.route('/signOffTailboardEmail/<token>', methods=['GET', 'POST'])
def signOffTailboardEmail(token):
    tailboard_user = Tailboard_Users.verify_sign_off_token(token)
    tailboard_user.sign_off_time = datetime.utcnow()
    db.session.commit()
    return redirect('/')

@app.route('/joinTailboardEmail/<token>', methods=['GET', 'POST'])
def joinTailboardEmail(token):
    tailboard_user = Tailboard_Users.verify_join_tailboard_token(token)
    tailboard_user.sign_on_time = datetime.utcnow()
    db.session.commit()
    sign_off_email(tailboard_user)
    return redirect('/')

@app.route('/refuseTailboardEmail/<token>', methods=['GET', 'POST'])
def refuseTailboardEmail(token):
    tailboard_user = Tailboard_Users.verify_refuse_tailboard_token(token)
    tailboard_user.sign_on_time = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    db.session.commit()
    return redirect('/')
    