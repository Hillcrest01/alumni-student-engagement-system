from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Interest, Event, Job
from app.forms import AdminAddUserForm, AdminEditUserForm
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin():
        abort(403)

@admin_bp.route('/dashboard')
def dashboard():
    # Get dashboard statistics
    stats = {
        'total_users': User.query.count(),
        'active_alumni': User.query.filter(
            User.role == 'alumni',
            User.availability == 'available'
        ).count(),
        'pending_verifications': User.query.filter_by(is_verified=False).count(),
        'pending_events_count': Event.query.filter_by(is_verified=False).count(),
        'pending_jobs_count': Job.query.filter_by(is_verified=False).count()
    }
    
    # Process pending events
    pending_events = []
    for event in Event.query.filter_by(is_verified=False).order_by(Event.date_time.asc()).all():
        pending_events.append({
            'id': event.id,
            'title': event.title,
            'creator': event.creator,
            'date_str': event.date_time.strftime('%Y-%m-%d'),
            'type': 'event'
        })
    
    # Process pending jobs
    pending_jobs = []
    for job in Job.query.filter_by(is_verified=False).order_by(Job.created_at.asc()).all():
        pending_jobs.append({
            'id': job.id,
            'title': job.title,
            'creator': job.creator,
            'date_str': job.created_at.strftime('%Y-%m-%d'),
            'type': 'job'
        })
    
    # Combine and sort all pending items
    all_pending = sorted(
        pending_events + pending_jobs,
        key=lambda x: x['date_str'],
        reverse=True
    )
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         pending_events=pending_events,
                         pending_jobs=pending_jobs,
                         all_pending=all_pending)

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


#jobs starts here
@admin_bp.route('/approve-job/<int:job_id>', methods=['POST'])
def approve_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_verified = True
    db.session.commit()
    flash(f'Job "{job.title}" approved successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job post deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/pending-jobs')
def list_jobs_pending():
    pending_jobs = Job.query.filter_by(is_verified=False).all()
    return render_template('admin/pending_jobs.html', jobs=pending_jobs)
