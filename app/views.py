from flask import Blueprint, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from app.models import User, Interest

views_bp = Blueprint('views', __name__)

@views_bp.route('/matches')
@login_required
def view_matches():
    if current_user.role != 'student':
        return redirect(url_for('auth.profile'))
    
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