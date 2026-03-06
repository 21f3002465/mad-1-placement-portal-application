
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import db, user

auth_bp = Blueprint('authenticate', __name__ )

# Registration

# @auth_bp.route('/', methods=['GET', 'POST'])
# def home():
#     return render_template('base.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

    # Checking wheather the username exists in the database
        if user.query.filter_by(username =  username).first():
            flash('This username already exists', 'danger')
            return redirect(url_for('authenticate.register'))

        
        new_user = user(username=username, email=email,  password=password, role=role)
        if role == 'student' : new_user.is_approved = True #Students can self register and Login
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('authenticate.login'))
    return render_template('register.html')

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST': 
        # when runnung the app, check the order if any error throws up
        email = request.form.get('email')
        password =  request.form.get('password')
        User = user.query.filter_by(email=email).first()

        if User and User.password == password:
            if User.role == 'company' and not User.is_approved:
                flash('Pending Approval', 'warning')
                return redirect(url_for('authenticate.login'))
            
            # When approved
            login_user(User)
            return redirect(url_for('views.dashboard'))
        
           # Checking wheather the username exists in the database

        # When credentials are invalid
        flash("Invalid Credentials, Please try again", 'danger')
    return render_template("login.html")


# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authenticate.login'))