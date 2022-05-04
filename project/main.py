from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserContainer,Container
from . import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # get the containerids the user has access too
    if current_user.admin:
        containers = Container.query.all()
    else:
        users_container_ids = [r.containerId for r in UserContainer.query.filter(UserContainer.userId == User.id).all()]
        containers = Container.query.filter(Container.id.in_(users_container_ids)).all()

    packed_containers = [(r.id,r.name) for r in containers]
    return render_template('index.html', containers = packed_containers)


