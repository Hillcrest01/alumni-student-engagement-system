from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models import User, Interest
from app.forms import LoginForm, ChangePasswordForm, CompleteProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

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
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))


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
    if current_user.profile_complete:
        return redirect(url_for('auth.profile'))
    
    form = CompleteProfileForm()
    form.interests.choices = [(i.id, i.name) for i in Interest.query.all()]
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.github_url = form.github_url.data
        
        if current_user.role == 'alumni':
            current_user.current_position = form.current_position.data
            current_user.company = form.company.data
        elif current_user.role == 'student':
            current_user.graduation_year = form.graduation_year.data
        
        # Update interests
        current_user.interests = Interest.query.filter(
            Interest.id.in_(form.interests.data)).all()
        
        current_user.profile_complete = True
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/complete_profile.html', form=form)