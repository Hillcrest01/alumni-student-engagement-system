from datetime import datetime
from app import db
from app.models import Event, Job
from app.utils import utc_to_eat
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort

main_bp = Blueprint('main', __name__)

def convert_event_for_display(event):
    """Convert Event model to display-friendly format"""
    return {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'date_time': event.date_time,
        'eat_datetime': utc_to_eat(event.date_time).strftime('%Y-%m-%d %H:%M'),
        'location': event.location,
        'image': event.image,
        'is_verified': event.is_verified,
        'creator': event.creator
    }

def convert_job_for_display(job):
    """Convert Job model to display-friendly format"""
    return {
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'job_type': job.job_type,
        'location': job.location,
        'application_link': job.application_link,
        'image': job.image,
        'created_at': job.created_at.strftime('%Y-%m-%d'),
        'is_verified': job.is_verified,
        'creator_id': job.creator_id,
        'creator': job.creator
        
    }

@main_bp.route('/')
def index():
    now = datetime.utcnow()
    
    # Get events
    upcoming_events = Event.query.filter(
        Event.date_time > now,
        Event.is_verified == True
    ).order_by(Event.date_time.asc()).limit(3).all()
    # Get jobs
    latest_jobs = Job.query.filter_by(is_verified=True).order_by(Job.created_at.desc()).limit(4).all()

    # Convert models for display
    converted_upcoming = [convert_event_for_display(e) for e in upcoming_events]
    converted_jobs = [convert_job_for_display(j) for j in latest_jobs]

    return render_template('index.html',
                         upcoming_events=converted_upcoming,
                         latest_jobs=converted_jobs,
                         current_time=now)