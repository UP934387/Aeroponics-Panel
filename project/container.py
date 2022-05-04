from flask import Blueprint, render_template, redirect, url_for, request, flash ,jsonify,json
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserContainer,Container,Sensor, Notification
from .serialcontrol import serialcom
from . import db

container = Blueprint('container', __name__, url_prefix='/container')


@container.route('/<int:id>')
@login_required
def containerpage(id):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))

    notifications = Notification.query.filter(Notification.containerId == id).filter(
                    Notification.seen == False).limit(4).all()

    packed_notifications = [(notification.id, notification.notification, notification.description) 
                            for notification in notifications]
    
    container = Container.query.filter(Container.id == id).first()
    return render_template('container.html', container = container, 
                            id = id, notifications = packed_notifications)

@container.route('/<int:id>/notification/<int:nid>/seen', methods=['POST'])
@login_required
def seennotification(id,nid):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))

    notification = Notification.query.filter(Notification.id == nid).first()
    notification.seen = True
    db.session.commit()
    return redirect(url_for('container.containerpage',container = container, id = id))

@container.route('/<int:id>/ph')
@login_required
def phdata(id):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))

    phdataArray = Sensor.query.filter(Sensor.containerId == id).filter(
                Sensor.unit == "PH").order_by(Sensor.id.desc()).limit(50).all()

    labels = []
    data = []

    for phdata in phdataArray:
        labels.append(phdata.recordedTime.strftime("%m/%d/%y %H:%M:%S"))
        data.append(phdata.value)
        
    return jsonify(Labels=labels[::-1], Data=data[::-1])

@container.route('/<int:id>/ec')
@login_required
def ecdata(id):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))

    ecdataArray = Sensor.query.filter(Sensor.containerId == id).filter(
                Sensor.unit == "EC").order_by(Sensor.id.desc()).limit(50).all()

    labels = []
    data = []

    for ecdata in ecdataArray:
        labels.append(ecdata.recordedTime.strftime("%m/%d/%y %H:%M:%S"))
        data.append(ecdata.value)
        
    return jsonify(Labels=labels[::-1], Data=data[::-1])

@container.route('/<int:id>/temp')
@login_required
def temperaturedata(id):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))

    tempdataArray = Sensor.query.filter(Sensor.containerId == id).filter(
                Sensor.unit == "TEMP").order_by(Sensor.id.desc()).limit(50).all()

    labels = []
    data = []

    for tempdata in tempdataArray:
        labels.append(tempdata.recordedTime.strftime("%m/%d/%y %H:%M:%S"))
        data.append(tempdata.value)
        
    return jsonify(Labels=labels[::-1], Data=data[::-1])

@container.route('/<int:id>/psi')
@login_required
def pressuredata(id):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))

    psidataArray = Sensor.query.filter(Sensor.containerId == id).filter(
                Sensor.unit == "PSI").order_by(Sensor.id.desc()).limit(50).all()

    labels = []
    data = []

    for psidata in psidataArray:
        labels.append(psidata.recordedTime.strftime("%m/%d/%y %H:%M:%S"))
        data.append(psidata.value)
        
    return jsonify(Labels=labels[::-1], Data=data[::-1])

@container.route('/<int:id>/control')
@login_required
def control(id):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))
    container = Container.query.filter(Container.id == id).first()

    return render_template('container-control.html', container = container, id = id)



@container.route('/<int:id>/relay/<int:rid>', methods=['POST'])
@login_required
def relaycontrol(id,rid):
    pair = UserContainer.query.filter(UserContainer.userId == current_user.id).filter(
            UserContainer.containerId == id).first()
    if pair is None and not current_user.admin:
        # if user is not paired to container and not admin go back to main page
        return redirect(url_for('main.index'))
    container = Container.query.filter(Container.id == id).first()

    timer = request.form.get('relay-time')

    if timer != "":
        #send serial commands to mcu, timer needs 000 appended to make it microseconds
        serialcom(container.serialPort,"relay;timer;"+str(rid)+"|"+timer+"000")

    #if unset just enable
    serialcom(container.serialPort,"relay;enable;"+str(rid))

    return redirect(url_for('container.control', container = container, id = id))