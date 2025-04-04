from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Project, Funding, Notification, PROJECT_STATUS
from forms import ProjectReviewForm
from datetime import datetime, timedelta, timezone
from models.constants import ROLES

admin_bp = Blueprint('admin', __name__)

# Admin authorization decorator
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    # Preserve the name and docstring
    decorated_function.__name__ = f.__name__
    decorated_function.__doc__ = f.__doc__
    return decorated_function

# Redirect /admin to /admin/dashboard
@admin_bp.route('/')
@login_required
@admin_required
def admin_index():
    return redirect(url_for('admin.dashboard'))

# Admin dashboard
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'admin':
        flash('هذه الصفحة مخصصة للمسؤولين فقط', 'warning')
        return redirect(url_for('main.index'))
    
    # Get statistics for admin dashboard
    total_users = User.query.count()
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(status=PROJECT_STATUS['FUNDING']).count()
    completed_projects = Project.query.filter_by(status=PROJECT_STATUS['COMPLETED']).count()
    pending_projects = Project.query.filter_by(status=PROJECT_STATUS['PENDING']).count()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_projects=total_projects,
                          active_projects=active_projects,
                          completed_projects=completed_projects,
                          pending_projects=pending_projects)

# List all projects
@admin_bp.route('/projects')
@login_required
@admin_required
def projects():
    # Get filter parameters
    status = request.args.get('status', 'all')
    category = request.args.get('category', 'all')
    
    # Base query
    query = Project.query
    
    # Apply filters
    if status != 'all':
        query = query.filter_by(status=status)
    if category != 'all':
        query = query.filter_by(category=category)
    
    # Order by submission date
    projects = query.order_by(Project.submitted_at.desc()).all()
    
    return render_template('admin/projects.html', projects=projects, status=status, category=category)

# Review a project
@admin_bp.route('/projects/<int:project_id>/review', methods=['GET', 'POST'])
@login_required
@admin_required
def review_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if the project is in pending status
    if project.status != PROJECT_STATUS['PENDING']:
        flash('هذا المشروع ليس قيد المراجعة', 'warning')
        return redirect(url_for('admin.projects'))
    
    form = ProjectReviewForm()
    if form.validate_on_submit():
        project.status = form.status.data
        project.admin_notes = form.admin_notes.data
        project.reviewed_at = datetime.now(timezone.utc)
        
        # If approved, set funding start and end dates
        if form.status.data == PROJECT_STATUS['FUNDING']:
            project.funding_start_date = datetime.now(timezone.utc)
            # Default to 60 days funding period
            project.funding_end_date = datetime.now(timezone.utc) + timedelta(days=60)
        
        # Create notification for project owner
        notification = Notification(
            user_id=project.owner_id,
            title='تم مراجعة مشروعك',
            content=f'مشروعك "{project.title}" تم {("الموافقة عليه") if form.status.data == "funding" else ("رفضه")}. {form.admin_notes.data or ""}',
            notification_type='project_review',
            related_id=project.id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash('تم حفظ مراجعة المشروع بنجاح', 'success')
        return redirect(url_for('admin.projects'))
    
    return render_template('admin/review_project.html', project=project, form=form)

# List all users
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    # Get filter parameters
    role = request.args.get('role', 'all')
    
    # Base query
    query = User.query
    
    # Apply filters
    if role != 'all':
        query = query.filter_by(role=role)
    
    # Get users
    users = query.order_by(User.created_at.desc()).all()
    
    return render_template('admin/users.html', users=users, role=role)

# View user details
@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    
    # Get user's projects if they are a project owner
    projects = []
    if user.is_project_owner():
        projects = Project.query.filter_by(owner_id=user.id).all()
    
    # Get user's fundings if they are a funder
    fundings = []
    if user.is_funder():
        fundings = Funding.query.filter_by(funder_id=user.id).all()
    
    return render_template(
        'admin/user_detail.html',
        user=user,
        projects=projects,
        fundings=fundings
    )

# Create admin user (first-time setup)
@admin_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    # Check if any admin already exists
    if User.query.filter_by(user_type=ROLES['ADMIN']).first():
        flash('تم إعداد المسؤول بالفعل', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not email or not password or not confirm_password:
            flash('يرجى ملء جميع الحقول', 'danger')
            return render_template('admin/setup.html')
        
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة', 'danger')
            return render_template('admin/setup.html')
        
        # Create admin user
        admin = User(
            full_name=username,
            email=email,
            user_type=ROLES['ADMIN'],
            created_at=datetime.utcnow()
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        flash('تم إنشاء حساب المسؤول بنجاح', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('admin/setup.html')