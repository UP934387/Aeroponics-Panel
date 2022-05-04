import serial
from datetime import datetime
from .models import Container, Sensor,Notification
from . import SENSOR_POLL
from . import db
import threading


def readsensors(app): 
    # must provide app context to use sqlalchemy
    with app.app_context():
        print("Polling MCU...")
        # fetch all serial ports containers are on
        containers = Container.query.with_entities(Container.id,Container.serialPort).all()
        for container in containers:
            # must extract the tuples to get the values
            id = container[0]
            port = container[1]

            line = serialcom(port,"sensorsread")
            # line none due to os error or # from another serial output that is not sensor data
            if line is None: 
                continue
            if line[0] == "#":
                continue
            # replace | with : so can be split without using RE
            _, temp, _, level, _, ph, _, ec, _, psi = line.replace("|",":").split(":")

            # create the sensor data for database using parsed data
            tempsensor = Sensor(containerId = id, unit="TEMP", value=temp,recordedTime=datetime.now())
            levelsensor = Sensor(containerId = id, unit="LEVEL", value=level,recordedTime=datetime.now())
            phsensor = Sensor(containerId = id, unit="PH", value=ph,recordedTime=datetime.now())
            ecsensor = Sensor(containerId = id, unit="EC", value=ec,recordedTime=datetime.now())
            psisensor = Sensor(containerId = id, unit="PSI", value=psi,recordedTime=datetime.now())

            if int(level) == 0:
                # check if a notification for this event has already been added to DB
                last_notification = Notification.query.filter(Notification.containerId == id).filter(
                                Notification.notification == "Water Level Is Low").filter(Notification.seen == False).first()
                # if no notification exists create one
                if last_notification is None:
                    notification = Notification(containerId = id, notification = "Water Level Is Low", 
                                description = "Fill Unit up with water", seen = False, created_at = datetime.now())
                    db.session.add(notification)

            if float(temp) > 30:
                # check if a notification for this event has already been added to DB
                last_notification = Notification.query.filter(Notification.containerId == id).filter(
                                Notification.notification == "Water is too hot").filter(Notification.seen == False).first()
                # if no notification exists create one
                if last_notification is None:
                    notification = Notification(containerId = id, notification = "Water is too hot", 
                                description = "Cool down water report incident", seen = False, created_at = datetime.now())
                    db.session.add(notification)

            if float(psi) > 105:
                # check if a notification for this event has already been added to DB
                last_notification = Notification.query.filter(Notification.containerId == id).filter(
                                Notification.notification == "Pressure is too high").filter(Notification.seen == False).first()
                # if no notification exists create one
                if last_notification is None:
                    notification = Notification(containerId = id, notification = "Pressure is too high", 
                                description = "Check system report incident", seen = False, created_at = datetime.now())
                    db.session.add(notification)

            # add new sensor data to session
            db.session.add(tempsensor)
            db.session.add(levelsensor)
            db.session.add(phsensor)
            db.session.add(ecsensor)
            db.session.add(psisensor)
            # commit to db
            db.session.commit()
        thread = threading.Timer(SENSOR_POLL, readsensors, [app])
        thread.start()  


def serialcom(port, command):
    try:
        # ensure timeout to prevent blocking
        ser = serial.Serial(port=port, timeout=3)
        # encode to bytes
        ser.write(command.encode()) 
        # read new line, strip newline, decode to ascii
        buffer = ser.readline().strip().decode('ascii')
        print(buffer)
        ser.close()
        return buffer
    except OSError as error:
        # either port already in use, device not conncted, incorrect port
        print(error)
        return None
