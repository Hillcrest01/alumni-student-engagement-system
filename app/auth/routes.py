from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models import User, Interest, Event
from app.utils import utc_to_eat
from app.forms import LoginForm, ChangePasswordForm, CompleteProfileForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    # Get first 5 upcoming verified events
    now = datetime.utcnow()
    upcoming_events = Event.query.filter(
        Event.date_time > now,
        Event.is_verified == True
    ).order_by(Event.date_time.asc()).limit(5).all()

    # Convert events for display
    converted_events = []
    for event in upcoming_events:
        converted = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'eat_datetime': utc_to_eat(event.date_time).strftime('%Y-%m-%d %H:%M'),
            'location': event.location,
            'image': event.image,
            'creator_id': event.creator_id
        }
        converted_events.append(converted)

    return render_template('index.html', upcoming_events=converted_events)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_verified:
            flash('Account not verified. Please contact admin.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=True)
        flash(f'Welcome back, {user.email}!', 'success')
        
        # Force password change if using temporary password
        if not user.password_changed:
            return redirect(url_for('auth.change_password'))
        
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.new_password.data)
        current_user.password_changed = True
        db.session.commit()
        
        flash('Password updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    form = CompleteProfileForm()
    form.interests.choices = [(i.id, i.name) for i in Interest.query.all()]
    
    # Pre-populate existing data
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio
        form.linkedin_url.data = current_user.linkedin_url
        form.github_url.data = current_user.github_url
        form.current_position.data = current_user.current_position
        form.company.data = current_user.company
        form.graduation_year.data = current_user.graduation_year
        form.interests.data = [i.id for i in current_user.interests]
    
    if form.validate_on_submit():
        # Update user logic
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.github_url = form.github_url.data
        
        if current_user.role == 'alumni':
            current_user.current_position = form.current_position.data
            current_user.company = form.company.data
        elif current_user.role == 'student':
            current_user.graduation_year = form.graduation_year.data
        
        current_user.interests = Interest.query.filter(
            Interest.id.in_(form.interests.data)
        ).all()
        
        current_user.profile_complete = True
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/complete_profile.html', form=form)

@auth_bp.route('/update-availability', methods=['POST'])
@login_required
def update_availability():
    if current_user.role != 'alumni':
        abort(403)
    
    new_status = request.form.get('availability')
    if new_status not in ['available', 'away']:
        flash('Invalid availability status', 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.availability = new_status
    current_user.last_active = datetime.utcnow()
    db.session.commit()
    
    flash('Availability status updated!', 'success')
    return redirect(url_for('auth.profile'))