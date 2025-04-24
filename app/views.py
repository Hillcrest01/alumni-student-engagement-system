from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import login_required, current_user
from app.models import User, Interest, Event, ContactMessage, Announcement
from datetime import datetime
from app.utils import utc_to_eat
from app import db
from app.forms import ContactForm, ContactFormLoggedIn

views_bp = Blueprint('views', __name__)

@views_bp.route('/matches')
@login_required
def view_matches():
    # if current_user.role != 'student':
    #     return redirect(url_for('auth.profile'))
    
    # Get student's interests
    student_interests = {i.id for i in current_user.interests}
    
    # Find matching available alumni
    matches = User.query.filter(
        User.role == 'alumni',
        User.availability == 'available',
        User.interests.any(Interest.id.in_(student_interests))
    ).all()
    
    # Calculate match score
    for alum in matches:
        alum.match_score = len({i.id for i in alum.interests} & student_interests)
    
    # Sort by match score and last active time
    matches.sort(key=lambda x: (-x.match_score, x.last_active), reverse=True)
    
    return render_template('matches.html', matches=matches)


@views_bp.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@views_bp.route('/learning' , methods=['GET', 'POST'])
def learning():
    return render_template('learning.html')

@views_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if current_user.is_authenticated:
        form = ContactFormLoggedIn()
    else:
        form = ContactForm()

    if form.validate_on_submit():
        if current_user.is_authenticated:
            message = ContactMessage(
                email=current_user.email,
                message=form.message.data,
                user_id=current_user.id
            )
        else:
            message = ContactMessage(
                name=form.name.data,
                email=form.email.data,
                message=form.message.data
            )
        
        db.session.add(message)
        db.session.commit()
        
        flash('Your message has been sent successfully! We will respond soon.', 'success')
        return redirect(url_for('views.contact'))

    return render_template('contact.html', form=form)

@views_bp.route('/admin/contact-messages')
@login_required
def contact_messages():
    if not current_user.is_admin:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))
    
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/contact_messages.html', messages=messages)

@views_bp.route('/admin/contact-messages/<int:message_id>/reply', methods=['POST'])
@login_required
def reply_to_message(message_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('main.index'))
    
    message = ContactMessage.query.get_or_404(message_id)
    response = request.form.get('response')
    
    if response:
        message.response = response
        message.is_responded = True
        message.is_read = True
        db.session.commit()
        
        # Here you would add code to actually send the email response
        # using Flask-Mail or another email service
        
        flash('Response sent successfully!', 'success')
    else:
        flash('Response cannot be empty', 'danger')
    
    return redirect(url_for('views.contact_messages'))

@views_bp.route('/announcements')
@login_required
def user_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('announcements.html', announcements=announcements)

