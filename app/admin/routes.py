from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Interest, Event
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
        'pending_events_count': Event.query.filter_by(is_verified=False).count()
    }
    
    # Get pending events for approval
    pending_events = []
    for event in Event.query.filter_by(is_verified=False).order_by(Event.date_time.asc()).all():
        pending_events.append({
            'id': event.id,
            'title': event.title,
            'creator': event.creator,
            'date_time': event.date_time.strftime('%Y-%m-%d'),  # Format here
            'raw_date': event.date_time  # Keep original for sorting if needed
        })
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         pending_events=pending_events)

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