from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import Job
from app.forms import JobForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app.utils import utc_to_eat

jobs_bp = Blueprint('jobs', __name__)

def convert_job_for_display(job):
    return {
        'id': job.id,
        'title': job.title,
        'description': job.description,
        'company': job.company,
        'job_type': job.job_type,
        'location': job.location,
        'application_link': job.application_link,
        'image': job.image,
        'created_at': job.created_at.strftime('%Y-%m-%d'),
        'is_verified': job.is_verified,
        'creator': job.creator
    }

@jobs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_job():
    form = JobForm()
    
    if form.validate_on_submit():
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads/')
        os.makedirs(os.path.join(upload_folder, 'jobs'), exist_ok=True)

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(upload_folder, 'jobs', filename)
            form.image.data.save(filepath)
            image_url = f"jobs/{filename}"
        else:
            image_url = None
            
        job = Job(
            title=form.title.data,
            description=form.description.data,
            company=form.company.data,
            job_type=form.job_type.data,
            location=form.location.data,
            application_link=form.application_link.data,
            image=image_url,
            creator_id=current_user.id,
            is_verified=not current_user.is_student()
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted!' + (' Awaiting admin approval.' if current_user.is_student() else ''), 'success')
        return redirect(url_for('jobs.job_list'))
    
    return render_template('jobs/create.html', form=form)

@jobs_bp.route('/')
def job_list():
    jobs = Job.query.filter_by(is_verified=True).order_by(Job.created_at.desc()).all()
    converted_jobs = [convert_job_for_display(job) for job in jobs]
    return render_template('jobs/list.html', jobs=converted_jobs)

@jobs_bp.route('/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('jobs/detail.html', job=convert_job_for_display(job))

@jobs_bp.route('/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if not (current_user.is_admin() or job.creator_id == current_user.id):
        abort(403)
        
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully', 'success')
    return redirect(url_for('jobs.job_list'))

@jobs_bp.route('/<int:job_id>/update', methods=['GET', 'POST'])
@login_required
def update_job(job_id):
    job = Job.query.get_or_404(job_id)
    if not (current_user.is_admin() or job.creator_id == current_user.id):
        abort(403)
    
    form = JobForm(obj=job)
    
    if form.validate_on_submit():
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'jobs', filename)
            form.image.data.save(filepath)
            job.image = f"jobs/{filename}"
        
        job.title = form.title.data
        job.description = form.description.data
        job.company = form.company.data
        job.job_type = form.job_type.data
        job.location = form.location.data
        job.application_link = form.application_link.data
        
        db.session.commit()
        flash('Job updated successfully', 'success')
        return redirect(url_for('jobs.job_detail', job_id=job.id))
    
    return render_template('jobs/update.html', form=form, job=convert_job_for_display(job))