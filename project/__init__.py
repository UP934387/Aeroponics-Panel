from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import threading
import atexit


SENSOR_POLL = 10 #seconds
# init SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'aeroponics'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    from .serialcontrol import readsensors


    def interrupt():
        global thread
        thread.cancel()

    def sensorsStart(app):
        global thread
        thread = threading.Timer(SENSOR_POLL, readsensors, [app])
        thread.start() 

    sensorsStart(app)
    atexit.register(interrupt)

    @login_manager.user_loader
    def load_user(user_id):
        # user_id is the primary key of user table, used in the query for user
        return User.query.get(int(user_id))

    # blueprint for auth routes in app
    from .auth import auth
    app.register_blueprint(auth)

    # blueprint for profile routes in app
    from .profile import profile
    app.register_blueprint(profile)

    # blueprint for admin routes in app
    from .admin import admin
    app.register_blueprint(admin)

    # blueprint for container routes in app
    from .container import container
    app.register_blueprint(container)

    # blueprint for other
    from .main import main
    app.register_blueprint(main)

    return app