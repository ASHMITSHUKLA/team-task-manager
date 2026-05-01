from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Project, Task

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    total_projects = Project.query.count()
    pending_tasks = Task.query.filter_by(assigned_to=current_user.id, status='todo').count()
    return render_template('dashboard.html', 
                         total_projects=total_projects, 
                         pending_tasks=pending_tasks)