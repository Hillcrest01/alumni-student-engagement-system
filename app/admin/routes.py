from flask import Blueprint, render_template
from flask_login import login_required
from app.models import User
from flask import abort
from flask_login import current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin():
        abort(403)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Temporary implementation
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)