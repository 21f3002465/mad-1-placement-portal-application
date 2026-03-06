import os 
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from models import db, user, application, placementdrive, company
from sqlalchemy import or_
from datetime import datetime

views_bp = Blueprint('views', __name__)

# If user is blacklisted, then it will be removed immediately
@views_bp.before_request # runs before each request is processed, gets executed before view function
def check_blacklisted():
    if current_user.is_authenticated and current_user.is_blacklisted:
        logout_user()
        flash("Your account has been suspended", 'danger')
        return redirect(url_for('authenticate.login'))
    
# Dashboard


# Dependending on the current user's role, redirect them to their respective dashboards
@views_bp.route('/')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('views.admin_dash'))
    if current_user.role == 'company':
        return redirect(url_for('views.company_dash'))
    if current_user.role == 'student':
        return redirect(url_for('views.student_dash'))

#Admin

@views_bp.route('/admin', methods=['GET'])
@login_required
def admin_dash():
    if current_user.role != 'admin':
        return redirect(url_for('views.dashboard'))
    
    search_query = request.args.get('q', "")
    if search_query:
        users=user.query.filter(or_(user.username.ilike(f'%{search_query}'), user.role.ilike(f'%{search_query}'))).all()
    else:
        users = user.query.all()

    students = [u for u in users if u.role == 'student']
    company = [u for u in users if u.role == 'company']
    pending_company = [u for u in users if not u.is_approved]

    pending_drives = placementdrive.query.filter_by(is_approved = False).all()

    chart_data = {'labels': ['company', 'students'], 'data':[len(company), len(students)]}
    return render_template('admin_dash.html',
                           students=students,
                           company=company,
                           pending_company=pending_company,
                           pending_drives=pending_drives,
                           search_query=search_query,
                           chart_data=chart_data)


@views_bp.route('/admin/<int:id>')
@login_required
def approve_company(id):
     if current_user.role != 'admin':
        return redirect(url_for('views.dashboard'))
     
     User = user.query.get_or_404(id)
     User.is_approved=True
     db.session.commit()
     flash('Approved!', 'success')
     return redirect(url_for('views.admin_dash'))

@views_bp.route('/toogle_blacklist/<int:user_id>')
@login_required
def toogle_blacklist(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('views.dashboard'))
    User = user.query.get_or_404(user_id)
    if User.role == "admin":
        flash('Admin cannot be blacklisted')
        return redirect(url_for('views.admin_dash'))
    
    User.is_blacklisted = not User.is_blacklisted
    db.session.commit()

    if User.is_blacklisted:
         status = "blacklisted"
    else:
         "restored"

    flash(f"User {User} is {status}", 'success')
    return redirect(url_for('views.admin_dash'))


@views_bp.route('/approve_drives/<int:d_id>')
@login_required
def approve_drive(d_id):
     if current_user.role != 'admin':
        return redirect(url_for('views.dashboard'))
     
     drive = placementdrive.query.get_or_404(d_id)
     drive.is_approved=True
     db.session.commit()
     flash('Approved placement drive !', 'success')
     return redirect(url_for('views.admin_dash'))
         

@views_bp.route('/company', methods = ['GET', 'POST'])
@login_required
def company_dash():
    # View drives creted by the company
    my_drives = placementdrive.query.filter_by(company_id = current_user.id).all() # need to show from database
    pending_drives = [d for d in my_drives if not d.is_approved]

    # drive_id = [drive.drive_id for drive in my_drives]

    return render_template('company_dash.html', my_drives=my_drives, pending_drives=pending_drives)

# company can view its own dasboard after login
@views_bp.route('/company_profile', methods = ['GET', 'POST'])
def company_profile():
    if current_user.role != 'company':
        return redirect(url_for('views.dashboard'))
    
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        HR_contact = request.form.get('HR_contact')
        website = request.form.get('website')
        company_id = current_user.id
        status = current_user.is_approved

        new_company = company(company_id=company_id, company_name=company_name, HR_contact=HR_contact, website=website, status=status)
        db.session.add(new_company)
        db.session.commit()
        flash('submitted', 'success')
        return redirect(url_for('views.company_dash'))
    return render_template('company_profile.html')


@views_bp.route('/create_drive', methods = ['GET', 'POST'])
def create_drive():
    if current_user.role != 'company':
        return redirect(url_for('views.dashboard'))
    
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        application_deadline = request.form.get('application_deadline')
        eligibility_criteria = request.form.get('eligibility_criteria')
        company_id = current_user.id

        application_deadline_date = datetime.fromisoformat(application_deadline)

        new_drive = placementdrive(job_title=job_title, job_description=job_description,  eligibility_criteria=eligibility_criteria, application_deadline=application_deadline_date, company_id=company_id)

        db.session.add(new_drive)
        db.session.commit()
        flash("new drive created successfully", 'success')
        return redirect(url_for('views.company_dash'))
    return render_template('create_drive.html')
    
# @views_bp.route('/update_application/<int:app_id>/<string:action>')
# @login_required
# def update_application(app_id, action):
#     # action = request.args.get('action')
#     if current_user.role != 'company':
#         return redirect(url_for('views.dashboard'))
    
#     # Qery the application
#     Application = application.query.get_or_404(app_id)
#     # application for a drive which is created by the company is the current user
#     if Application.placementdrive.company_id == current_user.id:  
#         if action == 'accept':
#             Application.status = 'Accepted' 
#         else:   
#             Application.status = 'Rejected'
#         db.session.commit()        
#     return redirect(url_for('views.company_dash'))


@views_bp.route('/update_app/<int:app_id>/<string:action>')
@login_required
def update_application(app_id, action):
    if current_user.role != 'company':
        return redirect(url_for('views.dashboard'))
    
    Application = application.query.get_or_404(app_id)    
    if action == 'accept':
        Application.status = 'Accepted'
    else:
        Application.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('views.company_dash'))    



# Student     

@views_bp.route('/student', methods = ['GET', 'POST'])
@login_required
def student_dash():
    if current_user.role != 'student':
        redirect(url_for('views.dashboard'))

    available_drives = placementdrive.query.filter_by(is_approved=True).all()

    #student application history
    my_application = application.query.filter_by(student_id  = current_user.id).all()
    return render_template('student_dash.html', available_drives=available_drives, my_application=my_application)

@views_bp.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
def apply_drives(drive_id):
     current_date = datetime.now()
     if current_user.role != 'student':
        return redirect(url_for('views.dashboard'))
     if not application.query.filter_by(student_id = current_user.id, drive_id=drive_id).first():
         db.session.add(application(student_id = current_user.id, drive_id = drive_id, application_date = current_date))
         db.session.commit()
         flash("applied successfully", 'success')
     return redirect(url_for('views.student_dash'))
        
#student profile
@views_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student':
        return redirect(url_for('views.dashboard'))
    
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename.endswith(('.pdf', '.docx')):
            filename = secure_filename(f"user_{current_user.id}") 
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            current_user.resume_file = filename
            db.session.commit()

            flash('Resume uploaded', 'success')
        return redirect(url_for('views.student_dash'))
    return render_template('profile.html')

  # if request.method=="POST":
        #     status = request.form.get('status')
        #     if status == 'accept': app.status = True

        #     else:
        #         app.is_rejected ='Rejected' 