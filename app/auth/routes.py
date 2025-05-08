from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
"""
This module defines the routes for the authentication blueprint (`auth_bp`) in a Flask application.
It includes functionalities for user authentication, profile management, password management, and 
verification requests. Below is an overview of the routes and their purposes:
1. `/login`:
    - Handles user login functionality.
    - Validates user credentials, checks account verification, and manages login sessions.
2. `/logout`:
    - Logs out the currently authenticated user and redirects to the main page.
3. `/change-password`:
    - Allows authenticated users to change their password.
    - Validates the current password and updates the new password in the database.
4. `/forgot-password`:
    - Provides a form for users to request a password reset.
    - Sends a password reset email with a secure token if the email exists in the system.
5. `/reset-password/<token>`:
    - Handles password reset functionality using a secure token.
    - Validates the token, allows users to set a new password, and updates the database.
6. `/profile`:
    - Displays the profile page of the currently authenticated user.
7. `/complete-profile`:
    - Allows authenticated users to complete or update their profile information.
    - Handles both alumni and student-specific fields and updates the database.
8. `/update-availability`:
    - Allows alumni users to update their availability status (e.g., available or away).
    - Ensures only alumni can access this route and updates the user's availability status.
9. `/request-verification`:
    - Provides a form for users to request account verification.
    - Prevents duplicate requests and stores the verification request in the database.
This module relies on Flask extensions such as `flask_login` for session management, 
`flask_sqlalchemy` for database interactions, and `itsdangerous` for secure token generation.
It also uses custom forms, models, and utility functions defined in the application.
"""
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models import User, Interest, Event, VerificationRequest
from app.utils import utc_to_eat
from app.forms import LoginForm, ChangePasswordForm, CompleteProfileForm, VerificationForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from app.emails import send_email
from flask import current_app

auth_bp = Blueprint('auth', __name__)

RESET_TOKEN_EXPIRATION = 3600

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if email exists
        if not user:
            flash('No account found with this email address.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check password validity
        if not user.check_password(form.password.data):
            flash('Incorrect password. Please Try again', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if account is verified
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


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate password reset token
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(user.email, salt='password-reset-salt')
            
            # Send password reset email
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email(
                to=user.email,
                subject="Password Reset Instructions",
                template="password_reset_email.html",
                reset_url=reset_url,
                expiration_hours=RESET_TOKEN_EXPIRATION//3600
            )
        
        # Always show success to prevent email enumeration
        flash('If an account exists with that email, you will receive password reset instructions shortly.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=RESET_TOKEN_EXPIRATION
        )
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.password_changed = True
        db.session.commit()
        
        flash('Your password has been updated! Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)

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


@auth_bp.route('/request-verification', methods=['GET', 'POST'])
def request_verification():
    form = VerificationForm()
    
    if form.validate_on_submit():
        existing_request = VerificationRequest.query.filter_by(email=form.email.data).first()
        if existing_request:
            flash('This email already has a pending request', 'warning')
            return redirect(url_for('auth.request_verification'))
            
        new_request = VerificationRequest(email=form.email.data)
        db.session.add(new_request)
        db.session.commit()
        
        flash('Verification request submitted! We will contact you soon.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/request_verification.html', form=form)
