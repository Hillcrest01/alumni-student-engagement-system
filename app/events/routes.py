from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import Event
from app.forms import EventForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app.utils import utc_to_eat

events_bp = Blueprint('events', __name__)

def convert_event_for_display(event):
    """Convert event object to display-friendly format with EAT timestamps"""
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'date_time': event.date_time,
        'eat_datetime': utc_to_eat(event.date_time).strftime('%Y-%m-%d %H:%M'),
        'location': event.location,
        'image': event.image,
        'is_verified': event.is_verified,
        'creator': event.creator,
        'created_at': event.created_at,
    }

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from app.models import db, Event
from app.forms import EventForm

events_bp = Blueprint('events', __name__)

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    
    if form.validate_on_submit():
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads/')  # Default to static/uploads
        os.makedirs(os.path.join(upload_folder, 'events'), exist_ok=True)  # Ensure directory exists

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(upload_folder, 'events', filename)
            form.image.data.save(filepath)
            image_url = f"events/{filename}"
        else:
            image_url = None
            
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date_time=form.date_time.data,
            location=form.location.data,
            image=image_url,
            creator_id=current_user.id,
            is_verified=not current_user.is_student()
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created!' + (' Awaiting admin approval.' if current_user.is_student() else ''), 'success')
        return redirect(url_for('events.event_list'))
    
    return render_template('events/create.html', form=form)


@events_bp.route('/')
def event_list():
    now = datetime.utcnow()
    
    # Convert events to display format
    def convert_query(query):
        return [convert_event_for_display(e) for e in query]
    
    upcoming = convert_query(
        Event.query.filter(
            Event.date_time > now,
            Event.is_verified == True
        ).order_by(Event.date_time.asc()).all()
    )
    
    past = convert_query(
        Event.query.filter(
            Event.date_time <= now,
            Event.is_verified == True
        ).order_by(Event.date_time.desc()).all()
    )
    
    return render_template('events/list.html', 
                         upcoming=upcoming,
                         past=past,
                         current_time=now)

@events_bp.route('/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    converted_event = convert_event_for_display(event)
    return render_template('events/detail.html', event=converted_event)

@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if not (current_user.is_admin() or event.creator_id == current_user.id):
        abort(403)
        
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully', 'success')
    return redirect(url_for('events.event_list'))


@events_bp.route('/<int:event_id>/update', methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    if not (current_user.is_admin() or event.creator_id == current_user.id):
        abort(403)
    
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        # Handle image update
        if form.remove_image.data:
            event.image = None
        elif form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events', filename)
            form.image.data.save(filepath)
            event.image = f"events/{filename}"
        
        event.title = form.title.data
        event.description = form.description.data
        event.date_time = form.date_time.data
        event.location = form.location.data
        
        db.session.commit()
        flash('Event updated successfully', 'success')
        return redirect(url_for('events.event_detail', event_id=event.id))
    
    # Pre-populate form for GET request
    form.date_time.data = event.date_time
    return render_template('events/update.html', form=form, event=convert_event_for_display(event))