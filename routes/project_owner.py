from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Project, ProjectUpdate, Notification, Funding, PROJECT_STATUS
from forms import ProjectForm, ProjectUpdateForm, ProfileForm
import os
from datetime import datetime, timezone
import uuid

project_owner_bp = Blueprint('project_owner', __name__)

# Helper function to save uploaded files
def save_file(file, folder='projects'):
    if not file:
        return None
    
    # Generate unique filename to prevent collisions
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Create directory path - make sure we're saving to static/uploads
    directory = os.path.join(current_app.root_path, 'static', 'uploads', folder)
    os.makedirs(directory, exist_ok=True)
    
    # Save file
    file_path = os.path.join(directory, unique_filename)
    file.save(file_path)
    
    # Return relative path for database storage - this must match how url_for uses it
    return f'uploads/{folder}/{unique_filename}'

# Dashboard for project owners
@project_owner_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'project_owner':
        flash('هذه الصفحة مخصصة لأصحاب المشاريع فقط', 'warning')
        return redirect(url_for('main.index'))
    
    # Get user's projects
    projects = Project.query.filter_by(owner_id=current_user.id).all()
    
    # Calculate statistics
    total_funding = sum(project.current_funding for project in projects)
    active_projects = sum(1 for project in projects if project.status == PROJECT_STATUS['FUNDING'])
    funded_projects = sum(1 for project in projects if project.status in [PROJECT_STATUS['FUNDED'], PROJECT_STATUS['COMPLETED']])
    
    return render_template('project_owner/dashboard.html', 
                          projects=projects,
                          total_funding=total_funding,
                          active_projects=active_projects,
                          funded_projects=funded_projects)

# Create a new project
@project_owner_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def create_project():
    if not current_user.is_project_owner():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    form = ProjectForm()
    if form.validate_on_submit():
        # Handle image upload
        image_path = None
        if form.image.data:
            image_path = save_file(form.image.data, 'projects')
        
        # Create new project
        new_project = Project(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            funding_goal=form.funding_goal.data,
            expected_return=form.expected_return.data,
            image=image_path if image_path else 'default_project.jpg',
            status=PROJECT_STATUS['DRAFT'],
            owner_id=current_user.id
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        flash('تم إنشاء المشروع بنجاح', 'success')
        return redirect(url_for('project_owner.project_detail', project_id=new_project.id))
    
    return render_template('project_owner/submit.html', form=form, is_edit=False)

# Edit an existing project
@project_owner_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    if not current_user.is_project_owner():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if the project belongs to the current user
    if project.owner_id != current_user.id:
        flash('غير مصرح بتعديل هذا المشروع', 'danger')
        return redirect(url_for('project_owner.dashboard'))
    
    # Check if the project can be edited
    if project.status not in [PROJECT_STATUS['DRAFT'], PROJECT_STATUS['REJECTED']]:
        flash('لا يمكن تعديل المشروع في هذه المرحلة', 'warning')
        return redirect(url_for('project_owner.project_detail', project_id=project.id))
    
    form = ProjectForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_path = save_file(form.image.data, 'projects')
            project.image = image_path
        
        # Update project details
        project.title = form.title.data
        project.description = form.description.data
        project.category = form.category.data
        project.funding_goal = form.funding_goal.data
        project.expected_return = form.expected_return.data
        
        db.session.commit()
        
        flash('تم تحديث المشروع بنجاح', 'success')
        return redirect(url_for('project_owner.project_detail', project_id=project.id))
    
    # Pre-fill form with existing data
    if request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        form.category.data = project.category
        form.funding_goal.data = project.funding_goal
        form.expected_return.data = project.expected_return
    
    return render_template('project_owner/submit.html', form=form, project=project, is_edit=True)

# Submit project for review
@project_owner_bp.route('/projects/<int:project_id>/submit', methods=['POST'])
@login_required
def submit_project(project_id):
    if not current_user.is_project_owner():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if the project belongs to the current user
    if project.owner_id != current_user.id:
        flash('غير مصرح بتقديم هذا المشروع', 'danger')
        return redirect(url_for('project_owner.dashboard'))
    
    # Check if the project is in draft or rejected status
    if project.status not in [PROJECT_STATUS['DRAFT'], PROJECT_STATUS['REJECTED']]:
        flash('لا يمكن تقديم المشروع في هذه المرحلة', 'warning')
        return redirect(url_for('project_owner.project_detail', project_id=project.id))
    
    # Update project status and submitted date
    project.status = PROJECT_STATUS['PENDING']
    project.submitted_at = datetime.now(timezone.utc)
    
    # Create notification for admin
    admin_notification = Notification(
        user_id=1,  # Assuming admin user has ID 1
        title='مشروع جديد بحاجة للمراجعة',
        content=f'تم تقديم مشروع جديد "{project.title}" بواسطة {current_user.full_name} للمراجعة',
        notification_type='project_submission',
        related_id=project.id
    )
    
    db.session.add(admin_notification)
    db.session.commit()
    
    flash('تم تقديم المشروع للمراجعة بنجاح', 'success')
    return redirect(url_for('project_owner.project_detail', project_id=project.id))

# View project details
@project_owner_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    if not current_user.is_project_owner():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if the project belongs to the current user
    if project.owner_id != current_user.id:
        flash('غير مصرح بعرض هذا المشروع', 'danger')
        return redirect(url_for('project_owner.dashboard'))
    
    # Get project updates
    updates = ProjectUpdate.query.filter_by(project_id=project.id).order_by(ProjectUpdate.date.desc()).all()
    
    # Get funding information
    fundings = Funding.query.filter_by(project_id=project.id).order_by(Funding.date.desc()).all()
    
    return render_template(
        'project_owner/project_detail.html',
        project=project,
        updates=updates,
        fundings=fundings
    )

# Create project update
@project_owner_bp.route('/projects/<int:project_id>/update', methods=['GET', 'POST'])
@login_required
def create_update(project_id):
    if not current_user.is_project_owner():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if the project belongs to the current user
    if project.owner_id != current_user.id:
        flash('غير مصرح بإضافة تحديث لهذا المشروع', 'danger')
        return redirect(url_for('project_owner.dashboard'))
    
    # Check if the project is in a state where updates are allowed
    if project.status not in [PROJECT_STATUS['FUNDING'], PROJECT_STATUS['FUNDED'], PROJECT_STATUS['COMPLETED']]:
        flash('لا يمكن إضافة تحديثات للمشروع في هذه المرحلة', 'warning')
        return redirect(url_for('project_owner.project_detail', project_id=project.id))
    
    form = ProjectUpdateForm()
    if form.validate_on_submit():
        new_update = ProjectUpdate(
            project_id=project.id,
            title=form.title.data,
            content=form.content.data,
            update_type=form.update_type.data,
            date=datetime.now(timezone.utc)
        )
        
        db.session.add(new_update)
        
        # Create notifications for funders
        from models import Funding, User
        funders = db.session.query(User).join(Funding).filter(Funding.project_id == project.id).distinct().all()
        
        for funder in funders:
            notification = Notification(
                user_id=funder.id,
                title=f'تحديث جديد لمشروع {project.title}',
                content=f'تم نشر تحديث جديد "{new_update.title}" للمشروع الذي تدعمه',
                notification_type='project_update',
                related_id=project.id
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('تم نشر التحديث بنجاح', 'success')
        return redirect(url_for('project_owner.project_detail', project_id=project.id))
    
    return render_template('project_owner/create_update.html', form=form, project=project)

# Edit user profile
@project_owner_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_project_owner():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    form = ProfileForm()
    if form.validate_on_submit():
        # Handle profile image upload
        if form.profile_image.data:
            image_path = save_file(form.profile_image.data, 'profiles')
            current_user.profile_image = image_path
        
        # Update user details
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        
        db.session.commit()
        
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('project_owner.profile'))
    
    # Pre-fill form with existing data
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
    
    return render_template('project_owner/profile.html', form=form)