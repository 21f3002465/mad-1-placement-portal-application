import os
from flask import Flask, redirect, render_template, flash, request
from models import *
from authenticate import auth_bp
from views import views_bp
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)


login_manager = LoginManager()
login_manager.login_view = 'authenticate.login'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

# Loading user by id 
@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(views_bp)

with app.app_context():
    db.create_all()
    admin_user = user.query.filter_by(role = 'admin').first() # check wheather admin user exists
    if not admin_user:      
        admin_user = user(
            username = 'admin',
            email = 'admin@email.com',
            password = '1234',
            role = 'admin',
            is_approved = True
        )
         # object can have multiple roles, admin_role is an object of the role table.
        
        db.session.add(admin_user) # add the admin object in the role table, user_login table, user_role table

        db.session.commit()

if __name__=='__main__':
    app.run(debug=True)


 # admin_role = role.query.filter_by(role='admin').first()
    # if not admin_role:
    #     admin_role = role(role='admin')
    #     db.session.add(admin_role)

    # student_role = role.query.filter_by(role='student').first()
    # if not student_role:
    #     student_role = role(role='student')
    #     db.session.add(student_role)

    # company_role = role.query.filter_by(role='company').first()
    # if not company_role:
    #     company_role = role(role='company')
    #     db.session.add(company_role)

#  admin_role = role.query.filter_by(role='admin').first() # quering the role table
#         comapny_role = role.query.filter_by(role='company').first()