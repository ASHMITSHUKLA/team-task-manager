from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Task, Project, User
from datetime import datetime
from app.models import Task, Project, User, ProjectMember

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/project/<int:project_id>')
@login_required
def project_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    users = User.query.all()
    return render_template('tasks.html', project=project, tasks=tasks, users=users)

@tasks_bp.route('/create', methods=['POST'])
@login_required
def create():
    if current_user.role != 'admin':
        flash('Only Admin can create tasks!', 'danger')
        return redirect(url_for('projects.index'))

    project_id = request.form.get('project_id')
    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    assigned_to = request.form.get('assigned_to')

    if not title or not project_id:
        flash('Title and Project are required', 'danger')
        return redirect(url_for('projects.index'))
        # Only allow assigning to Members, not Admins
    if assigned_to:
        assignee = User.query.get(assigned_to)
        if assignee and assignee.role == 'admin':
            flash('You can only assign tasks to Members, not Admins!', 'danger')
            return redirect(url_for('tasks.project_tasks', project_id=project_id))    

    task = Task(
        title=title,
        description=description,
        due_date=datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
        project_id=project_id,
        assigned_to=assigned_to if assigned_to else None,
        created_by=current_user.id
    )

    db.session.add(task)
    db.session.commit()

    # Auto add the assignee to the project (so they can see it)
    if assigned_to:
        existing = ProjectMember.query.filter_by(project_id=project_id, user_id=assigned_to).first()
        if not existing:
            member = ProjectMember(project_id=project_id, user_id=assigned_to)
            db.session.add(member)
            db.session.commit()

    flash('Task created successfully!', 'success')
    return redirect(url_for('tasks.project_tasks', project_id=project_id))
@tasks_bp.route('/my-tasks')
@login_required
def my_tasks():
    tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    return render_template('my_tasks.html', tasks=tasks)    
@tasks_bp.route('/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get('status')
    
    if new_status in ['todo', 'inprogress', 'done']:
        task.status = new_status
        db.session.commit()
        flash('Task status updated!', 'success')
    
    return redirect(url_for('tasks.project_tasks', project_id=task.project_id))    