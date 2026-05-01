from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Project, ProjectMember

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        # Admin sees only his own created projects
        projects = Project.query.filter_by(created_by=current_user.id).all()
    else:
        # Member sees projects where he has at least one task assigned
        projects = Project.query.join(ProjectMember).filter(ProjectMember.user_id == current_user.id).all()
    return render_template('projects.html', projects=projects)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'admin':
        flash('Only Admin can create projects!', 'danger')
        return redirect(url_for('projects.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Project name is required!', 'danger')
            return redirect(url_for('projects.create'))

        new_project = Project(
            name=name,
            description=description,
            created_by=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()

        # Auto add creator
        db.session.add(ProjectMember(project_id=new_project.id, user_id=current_user.id))
        db.session.commit()

        flash('Project created successfully!', 'success')
        return redirect(url_for('projects.index'))

    return render_template('create_project.html')