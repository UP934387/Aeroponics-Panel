from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserContainer,Container
from . import db

profile = Blueprint('profile', __name__, url_prefix='/profile')

@profile.route('/')
@login_required
def profilepage():
    return render_template('profile.html')

@profile.route('/updateemail', methods=['POST'])
@login_required
def updateemail():
    email = request.form.get('email')
    password = request.form.get('password')

    if email == "":
        flash('Email is Not Set for Update')
        return redirect(url_for('profile.profilepage'))

    if password == "":
        flash('Password is Not Set for Update')
        return redirect(url_for('profile.profilepage'))

    # hash user supplied password and then compare to hashed password in the database
    if not check_password_hash(current_user.password, password):
        flash('Incorrect Password.')
        return redirect(url_for('profile.profilepage'))

    # if the user exists, this will be set
    user_of_new_email = User.query.filter(func.lower(User.email) == func.lower(email)).first()

    if user_of_new_email:
        # cant use the same email as another account
        flash('Email already in use.')
        return redirect(url_for('profile.profilepage'))

    # get the user record, update the email, commit back to db
    cur_user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
    cur_user.email = email
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))

@profile.route('/updatepassword', methods=['POST'])
@login_required
def updatepassword():
    old_password = request.form.get('old-password')
    new_password = request.form.get('new-password')
    confirm_password = request.form.get('confirm-new-password')

    if old_password == "":
        flash('Old Password is Not Set for Update')
        return redirect(url_for('profile.profilepage'))

    if new_password == "":
        flash('New Password is Not Set for Update')
        return redirect(url_for('profile.profilepage'))

    if confirm_password == "":
        flash('Confirmation password is Not Set for Update')
        return redirect(url_for('profile.profilepage'))

    # hash user supplied password and then compare to hashed password in the database
    if not check_password_hash(current_user.password, old_password):
        flash('Incorrect Password.')
        return redirect(url_for('profile.profilepage'))

    if new_password != confirm_password:
        # new password missmatch
        flash('New Password Does Not Match.')
        return redirect(url_for('profile.profilepage'))

     # if the password is less than 8 characters reject the new account for security
    if len(new_password) < 8:
        flash('Password must be greater than 8 characters')
        return redirect(url_for('profile.profilepage'))

    # get the user record, hash password, update the password, commit back to db. ensure case insenstive
    cur_user = User.query.filter(func.lower(User.email) == func.lower(current_user.email)).first()
    cur_user.password = generate_password_hash(new_password, method='sha256')
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))

@profile.route('/deleteaccount', methods=['POST'])
@login_required
def deleteaccount():
    password = request.form.get('password')

    if password == "":
        flash('Password is Not Set for Delete')
        return redirect(url_for('profile.profilepage'))

    # hash user supplied password and then compare to hashed password in the database
    if not check_password_hash(current_user.password, password):
        flash('Incorrect Password.')
        return redirect(url_for('profile.profilepage'))

    #delete the user
    User.query.filter(func.lower(User.email) == func.lower(current_user.email)).delete()
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))
