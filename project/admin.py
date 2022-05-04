from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserContainer,Container
from . import db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@login_required
def adminpage():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        return redirect(url_for('auth.login'))
    else:
        return render_template('admin.html')

@admin.route('/addcontainer', methods=['POST'])
@login_required
def addcontainer():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))

    container_name = request.form.get('container')
    container_port = request.form.get('serial')

    if container_name == "":
        flash('Container Name is Not Set for Edit')
        return redirect(url_for('admin.adminpage'))

    if container_port == "":
        flash('Container Port is Not Set for Edit')
        return redirect(url_for('admin.adminpage'))

    container = Container.query.filter(func.lower(Container.name) == func.lower(container_name)).first()
    port = Container.query.filter(func.lower(Container.serialPort) == func.lower(container_port)).first()

    if container:
        #container exists and names are unique
        flash("Container name already in use")
        return redirect(url_for('admin.adminpage'))

    if port:
        #Serial port already used
        flash("Serial Port already in use")
        return redirect(url_for('admin.adminpage'))

    new_container = Container(name= container_name, serialPort= container_port)

    # add the new container to the database
    db.session.add(new_container)
    db.session.commit()
    return redirect(url_for('admin.adminpage'))

@admin.route('/editcontainer', methods=['POST'])
@login_required
def editcontainer():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))
        
    container_old_name = request.form.get('old_container')
    container_name = request.form.get('container')
    container_port = request.form.get('serial')

    # check the form has been filled out
    if container_old_name == "":
        flash('Old Container Name is Not Set for Edit')
        return redirect(url_for('admin.adminpage'))

    if container_name == "":
        flash('Container Name is Not Set for Edit')
        return redirect(url_for('admin.adminpage'))

    if container_port == "":
        flash('Container Port is Not Set for Edit')
        return redirect(url_for('admin.adminpage'))


    # use func.lower to ensure case is insensitive!
    container = Container.query.filter(func.lower(Container.name) == func.lower(container_old_name)).first()
    
    container_new_name = Container.query.filter(func.lower(Container.name) == func.lower(container_name)).first()
    port_new_port = Container.query.filter(func.lower(Container.serialPort) == func.lower(container_port)).first()

    if container is None:
        #container name doesnt exist
        flash("Invalid Container Name.")
        return redirect(url_for('admin.adminpage'))

    # if container new name is None then no container has that name
    # if the container new name is set but is the same as the current container all is good
    if container_new_name:
        if container_new_name.id != container.id:
            #container exists and names are unique
            flash("New Container name already in use")
            return redirect(url_for('admin.adminpage'))

    # if container new port is None then no container has that port
    # if the container new port is set but is the same as the current container all is good
    if port_new_port:
        if port_new_port.id != container.id:
            #Serial port already used
            flash("New Serial Port already in use")
            return redirect(url_for('admin.adminpage'))

    container.name = container_name
    container.serialPort = container_port

    db.session.commit()
    return redirect(url_for('admin.adminpage'))

@admin.route('/deletecontainer', methods=['POST'])
@login_required
def deletecontainer():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))
        
    container_name = request.form.get('container')

    if container_name == "":
        flash('Container Name is Not Set for Delete')
        return redirect(url_for('admin.adminpage'))

    container = Container.query.filter(func.lower(Container.name) == func.lower(container_name)).first()

    if container is None:
        #container id doesnt exist
        flash("Invalid Container Name.")
        return redirect(url_for('admin.adminpage'))

    Container.query.filter_by(id = container.id).delete()

    db.session.commit()
    return redirect(url_for('admin.adminpage'))

@admin.route('/createuser', methods=['POST'])
@login_required
def createuser():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))

    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    if email == "":
        flash('Email is Not Set for new user')
        return redirect(url_for('admin.adminpage'))

    if username == "":
        flash('Username is Not Set for new user')
        return redirect(url_for('admin.adminpage'))

    # if the password is less than 8 characters reject the new account for security
    if len(password) < 8:
        flash('Password must be greater than 8 characters')
        return redirect(url_for('admin.adminpage'))

    # Another user already uses this email address if this is not None
    user = User.query.filter_by(email=email).first()

    # if the user exists, reject the new account
    if user: 
        flash('Email address already exists')
        return redirect(url_for('admin.adminpage'))

    # create the new user from form data
    # password is hashed for security, do not store plaintext
    new_user = User(email=email, username=username, 
                password=generate_password_hash(password, method='sha256'), admin=False)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('admin.adminpage'))

@admin.route('/edituserpassword', methods=['POST'])
@login_required
def edituserpassword():

    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))

    email = request.form.get('email')
    new_password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')

    if email == "":
        flash('Email is Not Set for Update')
        return redirect(url_for('admin.adminpage'))

    if new_password == "":
        flash('New Password is Not Set for Update')
        return redirect(url_for('admin.adminpage'))

    if confirm_password == "":
        flash('Confirmation password is Not Set for Update')
        return redirect(url_for('admin.adminpage'))

    if new_password != confirm_password:
        # new password missmatch
        flash('New Password Does Not Match.')
        return redirect(url_for('admin.adminpage'))

     # if the password is less than 8 characters reject the new account for security
    if len(new_password) < 8:
        flash('Password must be greater than 8 characters')
        return redirect(url_for('admin.adminpage'))

    # get the user record, hash password, update the password, commit back to db. ensure case insenstive
    cur_user = User.query.filter(func.lower(User.email) == func.lower(email)).first()

    if cur_user is None:
        flash('User does not exist')
        return redirect(url_for('admin.adminpage'))

    cur_user.password = generate_password_hash(new_password, method='sha256')
    db.session.commit()

    return redirect(url_for('admin.adminpage'))

@admin.route('/deleteuser', methods=['POST'])
@login_required
def deleteuser():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))

    email = request.form.get('email')

    if email == "":
        flash('Email is Not Set for Delete')
        return redirect(url_for('admin.adminpage'))

    #delete the user
    User.query.filter(func.lower(User.email) == func.lower(email)).delete()
    db.session.commit()
    return redirect(url_for('admin.adminpage'))

@admin.route('/containerpairuser', methods=['POST'])
@login_required
def containerpairuser():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))

    container_name = request.form.get('container')
    email = request.form.get('email')

    if container_name == "":
        flash('Container Name is Not Set for Pairing')
        return redirect(url_for('admin.adminpage'))

    if email == "":
        flash('Email is Not Set for Pairing')
        return redirect(url_for('admin.adminpage'))

    # query the user and container records to get ids
    user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
    container = Container.query.filter(func.lower(Container.name) == func.lower(container_name)).first()

    # query the usercontainer record for the id of user and the container that will be added to ensure
    # its not already added
    pair = UserContainer.query.filter(UserContainer.userId == user.id).filter(UserContainer.containerId == container.id).first()
    if pair:
        # the user is already paired to the container throw error
        flash('User is already paired to that Container')
        return redirect(url_for('admin.adminpage'))

    #create the usercontainer record and write to db
    user_container_pair = UserContainer(userId = user.id, containerId = container.id)
    db.session.add(user_container_pair)
    db.session.commit()
    return redirect(url_for('admin.adminpage'))


@admin.route('/containerremoveuser', methods=['POST'])
@login_required
def containerremoveuser():
    isAdmin = current_user.admin
    if not isAdmin:
        # user is not an admin cannot use this route
        flash('Unauthorized.')
        return redirect(url_for('auth.login'))

    container_name = request.form.get('container')
    email = request.form.get('email')

    if container_name == "":
        flash('Container Name is Not Set for Removal')
        return redirect(url_for('admin.adminpage'))

    if email == "":
        flash('Email is Not Set for Removal')
        return redirect(url_for('admin.adminpage'))

    # query the user and container records to get ids
    user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
    container = Container.query.filter(func.lower(Container.name) == func.lower(container_name)).first()

    if user is None:
        flash('User does not exist')
        return redirect(url_for('admin.adminpage'))

    if container is None:
        flash('Container does not exist')
        return redirect(url_for('admin.adminpage'))

    user_container = UserContainer.query.filter(UserContainer.userId == user.id).filter(UserContainer.containerId == container.id)

    if user_container.first() is None:
        flash('Container is not paired to that User')
        return redirect(url_for('admin.adminpage'))

    # remove the record from the DB
    user_container.delete()
    db.session.commit()
    return redirect(url_for('admin.adminpage'))