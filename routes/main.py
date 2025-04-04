from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app import db  # Import db directly from app, not from models
from models import Project, User, Watchlist, PROJECT_STATUS, ProjectUpdate
from forms import ContactForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Featured projects (funded or funding)
    featured_projects = Project.query.filter(
        Project.status.in_([PROJECT_STATUS['FUNDING'], PROJECT_STATUS['FUNDED']])
    ).order_by(Project.funding_progress.desc()).limit(6).all()
    
    # Statistics for the homepage
    total_projects = Project.query.count()
    total_users = User.query.count()
    total_funding = db.session.query(db.func.sum(Project.current_funding)).scalar() or 0
    completed_projects = Project.query.filter_by(status=PROJECT_STATUS['COMPLETED']).count()
    
    return render_template('index.html', 
                          featured_projects=featured_projects,
                          total_projects=total_projects,
                          total_users=total_users,
                          total_funding=total_funding,
                          completed_projects=completed_projects)

@main_bp.route('/projects')
def projects():
    # Get filter parameters
    category = request.args.get('category', 'all')
    status = request.args.get('status', 'all')
    
    # Base query - only show approved projects (funding or funded)
    query = Project.query.filter(
        Project.status.in_([PROJECT_STATUS['FUNDING'], PROJECT_STATUS['FUNDED']])
    )
    
    # Apply category filter if specified
    if category != 'all':
        query = query.filter_by(category=category)
    
    # Apply status filter if specified
    if status != 'all':
        query = query.filter_by(status=PROJECT_STATUS[status.upper()])
    
    # Order by creation date (newest first)
    projects = query.order_by(Project.created_at.desc()).all()
    
    return render_template('projects.html', projects=projects)

@main_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Only show public projects
    if project.status not in [PROJECT_STATUS['FUNDING'], PROJECT_STATUS['FUNDED'], PROJECT_STATUS['COMPLETED']]:
        if not current_user.is_authenticated or (current_user.id != project.owner_id and not current_user.is_admin()):
            flash('هذا المشروع غير متاح للعرض حالياً', 'warning')
            return redirect(url_for('main.projects'))
    
    # Get project updates
    project.updates = ProjectUpdate.query.filter_by(project_id=project.id).order_by(ProjectUpdate.date.desc()).all()
    
    # Get similar projects (same category, excluding current)
    similar_projects = Project.query.filter(
        Project.category == project.category,
        Project.id != project.id,
        Project.status.in_([PROJECT_STATUS['FUNDING'], PROJECT_STATUS['FUNDED']])
    ).limit(3).all()
    
    return render_template('project_detail.html', project=project, similar_projects=similar_projects)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Here you would typically send an email or save the contact form to database
        # For now, just show a success message
        flash('تم إرسال رسالتك بنجاح، سنتواصل معك قريبًا', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', form=form)

@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')