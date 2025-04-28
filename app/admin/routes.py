from io import BytesIO
"""
This module defines the routes and functionalities for the admin section of the Alumni-Student Engagement System.
It includes features for managing users, events, jobs, verification requests, announcements, and generating reports.
Modules:
- `check_admin`: Restricts access to admin users only.
- `dashboard`: Displays the admin dashboard with system statistics and pending items.
- `manage_users`: Lists all users for management purposes.
- `add_user`: Allows the admin to add a new user with a temporary password.
- `edit_user`: Enables editing of user details by the admin.
- `delete_user`: Allows the admin to delete a user, with a restriction on deleting their own account.
- `verify_event`: Approves an event and notifies the creator via email.
- `delete_event`: Deletes an event from the system.
- `verify_events`: Lists all pending events for verification.
- `approve_job`: Approves a job post and notifies the creator via email.
- `delete_job`: Deletes a job post and notifies the creator via email.
- `list_jobs_pending`: Lists all pending job posts for verification.
- `verification_requests`: Displays all verification requests and their statuses.
- `handle_verification`: Handles approval or rejection of a verification request and notifies the user.
- `list_announcements`: Lists all announcements in the system.
- `create_announcement`: Allows the admin to create a new announcement.
- `edit_announcement`: Enables editing of an existing announcement.
- `delete_announcement`: Deletes an announcement from the system.
- `generate_report`: Generates a system report as a downloadable PDF file.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, Interest, Event, Job, VerificationRequest, Announcement
from app.forms import AdminAddUserForm, AdminEditUserForm
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.reports import generate_system_report
from app.emails import send_email  # Email integration

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


#restrict to admin users
@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin():
        abort(403)

@admin_bp.route('/dashboard')
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'active_alumni': User.query.filter(
            User.role == 'alumni',
            User.availability == 'available'
        ).count(),
        'pending_verifications': User.query.filter_by(is_verified=False).count(),
        'pending_events_count': Event.query.filter_by(is_verified=False).count(),
        'pending_jobs_count': Job.query.filter_by(is_verified=False).count(),
    }
    
    pending_requests_count = VerificationRequest.query.filter_by(status='pending').count()
    pending_events = []
    for event in Event.query.filter_by(is_verified=False).order_by(Event.date_time.asc()).all():
        pending_events.append({
            'id': event.id,
            'title': event.title,
            'creator': event.creator,
            'date_str': event.date_time.strftime('%Y-%m-%d'),
            'type': 'event'
        })
    
    pending_jobs = []
    for job in Job.query.filter_by(is_verified=False).order_by(Job.created_at.asc()).all():
        pending_jobs.append({
            'id': job.id,
            'title': job.title,
            'creator': job.creator,
            'date_str': job.created_at.strftime('%Y-%m-%d'),
            'type': 'job'
        })
    
    all_pending = sorted(
        pending_events + pending_jobs,
        key=lambda x: x['date_str'],
        reverse=True
    )
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         pending_events=pending_events,
                         pending_jobs=pending_jobs,
                         all_pending=all_pending , pending_requests_count=pending_requests_count)

@admin_bp.route('/users')
def manage_users():
    users = User.query.order_by(User.role, User.email).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/add-user', methods=['GET', 'POST'])
def add_user():
    form = AdminAddUserForm()
    
    if form.validate_on_submit():
        temp_password = "Password123!"
        user = User(
            email=form.email.data,
            role=form.role.data,
            password_hash=generate_password_hash(temp_password),
            is_verified=True if form.role.data == 'admin' else False
        )
        
        db.session.add(user)
        db.session.commit()

        #send the user details
        send_email(
            to=user.email,
            subject="Your Account has been Approved",
            template="new_user_account.html",
            user=user,
            temp_password=temp_password
        )
        
        flash(f'User added! Temporary password: {temp_password}', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/add_user.html', form=form)

@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm(obj=user)
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.role = form.role.data
        user.profile_complete = form.profile_complete.data
        user.is_verified = form.is_verified.data
        db.session.commit()
        
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/delete-user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/verify-event/<int:event_id>', methods=['POST'])
def verify_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.is_verified = True
    db.session.commit()
    
    # Send approval email
    send_email(
        to=event.creator.email,
        subject=f"Event Approved: {event.title}",
        template="event_approved.html",
        user=event.creator,
        event=event
    )
    
    flash(f'Event "{event.title}" approved successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/verify-events')
def verify_events():
    pending_events = Event.query.filter_by(is_verified=False).all()
    return render_template('admin/verify_events.html', events=pending_events)

@admin_bp.route('/approve-job/<int:job_id>', methods=['POST'])
def approve_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_verified = True
    db.session.commit()
    
    # Send approval email
    send_email(
        to=job.creator.email,
        subject=f"Job Approved: {job.title}",
        template="job_approved.html",
        user=job.creator,
        job=job
    )
    
    flash(f'Job "{job.title}" approved successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Access related info before deleting
    creator_email = job.creator.email
    job_title = job.title
    job_creator = job.creator

    # Now safe to delete
    db.session.delete(job)
    db.session.commit()

    # Now send the email using saved info
    send_email(
        to=creator_email,
        subject=f"Job Rejected: {job_title}",
        template="job_rejected.html",
        user=job_creator,
        job=job_title 
    )
    
    flash('Job post deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/pending-jobs')
def list_jobs_pending():
    pending_jobs = Job.query.filter_by(is_verified=False).all()
    return render_template('admin/pending_jobs.html', jobs=pending_jobs)

@admin_bp.route('/verification-requests')
@login_required
def verification_requests():
    requests = VerificationRequest.query.order_by(VerificationRequest.created_at.desc()).all()
    pending_requests_count = VerificationRequest.query.filter_by(status='pending').count()
    return render_template('admin/verification_requests.html', requests=requests , pending_requests_count=pending_requests_count)

@admin_bp.route('/verify-request/<int:request_id>/<status>')
@login_required
def handle_verification(request_id, status):
    v_request = VerificationRequest.query.get_or_404(request_id)
    
    if status not in ['approved', 'rejected']:
        abort(400)
    
    v_request.status = status
    v_request.reviewed_at = datetime.utcnow()
    v_request.admin_id = current_user.id
    
    if status == 'approved':
        user = User.query.filter_by(email=v_request.email).first()
        if user:
            user.is_verified = True
            send_email(
                to=user.email,
                subject="Account Verification Approved",
                template="emails/verification_approved.html",
                user=user
            )
    
    db.session.commit()
    
    flash(f'Request {status} successfully', 'success')
    return redirect(url_for('admin.verification_requests'))

@admin_bp.route('/announcements')
@login_required
def list_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)

@admin_bp.route('/announcements/create', methods=['GET', 'POST'])
@login_required
def create_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_announcement = Announcement(title=title, content=content)
        db.session.add(new_announcement)
        db.session.commit()
        flash('Announcement created successfully!', 'success')
        return redirect(url_for('admin.list_announcements'))
    return render_template('admin/create_announcement.html')

@admin_bp.route('/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    if request.method == 'POST':
        announcement.title = request.form['title']
        announcement.content = request.form['content']
        db.session.commit()
        flash('Announcement updated successfully!', 'success')
        return redirect(url_for('admin.list_announcements'))
    return render_template('admin/edit_announcement.html', announcement=announcement)

@admin_bp.route('/announcements/delete/<int:id>', methods=['POST'])
@login_required
def delete_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement deleted successfully!', 'success')
    return redirect(url_for('admin.list_announcements'))

@admin_bp.route('/generate-report', methods=['POST'])
def generate_report():
    report_type = request.form.get('report_type', 'full')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    pdf_buffer = generate_system_report(start_date, end_date)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'system_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    )