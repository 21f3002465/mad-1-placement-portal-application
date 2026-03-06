from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class user(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.VARCHAR, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_approved = db.Column(db.Boolean, default=False) # for alumni and company approval
    is_blacklisted = db.Column(db.Boolean, default=False) 
    resume_file = db.Column(db.String(100), nullable = True)

    placementdrives = db.relationship('placementdrive', backref = 'company', lazy=True)
    applications = db.relationship('application', backref='student', lazy=True)

class company(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.ForeignKey('user.id'), unique = True)
    company_name = db.Column(db.String(250), nullable=False)
    HR_contact = db.Column(db.Integer(), nullable=False)
    website = db.Column(db.VARCHAR(100), nullable=False)
    status = db.Column(db.ForeignKey('user.is_approved'))

    # placementdrive = db.relationship('application', backref = 'p', lazy = True)

class placementdrive(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.VARCHAR, db.ForeignKey('user.id'), nullable=False)#mentor_id
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.String(250), nullable=False)
    application_deadline = db.Column(db.Date(), nullable=False)
    eligibility_criteria = db.Column(db.String(250), nullable=False)
    is_approved = db.Column(db.Boolean, default=False) 

    applications = db.relationship('application', backref = 'Placementdrive', lazy=True)

class application(db.Model):

    id = db.Column(db.Integer,  primary_key=True)
    student_id = db.Column(db.ForeignKey('user.id')) 
    drive_id = db.Column(db.Integer, db.ForeignKey('placementdrive.id'), nullable =False) #session_id
    application_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(250), default="pending")

'''
* relationships help us add multiple columns with multiple tables 
* uselist is used for one to one mapping
* user can have multiple roles, so we created user role table. We can add simillarly multiple roles.
'''

# application_id = db.Column(db.Integer, unique=True, autoincrement=True, nullable=False) #session_id
# class role(db.Model):

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     role = db.Column(db.String(50), nullable=False)

# class user_role(db.Model):

#     id = db.Column(db.ForeignKey('user.id'), primary_key=True)
#     role = db.Column(db.ForeignKey('role.id'))