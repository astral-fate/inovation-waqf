from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Project, Funding, Watchlist, Notification, PROJECT_STATUS
from forms import FundingForm, ProfileForm
from datetime import datetime

funder_bp = Blueprint('funder', __name__)

@funder_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'funder':
        flash('هذه الصفحة مخصصة للداعمين/المستثمرين فقط', 'warning')
        return redirect(url_for('main.index'))
    
    # Get user's fundings and watchlist
    fundings = Funding.query.filter_by(user_id=current_user.id).all()
    watchlist_projects = Watchlist.query.filter_by(user_id=current_user.id).all()
    
    # Calculate total contributions
    total_contributions = sum(funding.amount for funding in fundings)
    
    # Get projects the user has funded
    funded_projects = []
    for funding in fundings:
        project = Project.query.get(funding.project_id)
        if project:
            funded_projects.append(project)
    
    # Count active and completed projects
    active_projects = sum(1 for project in funded_projects if project.status in [PROJECT_STATUS['FUNDING'], PROJECT_STATUS['FUNDED']])
    completed_projects = sum(1 for project in funded_projects if project.status == PROJECT_STATUS['COMPLETED'])
    
    return render_template('funder/dashboard.html',
                          fundings=fundings,
                          watchlist_projects=watchlist_projects,
                          total_contributions=total_contributions,
                          funded_projects=funded_projects,
                          active_projects=active_projects,
                          completed_projects=completed_projects)

# Fund a project
@funder_bp.route('/projects/<int:project_id>/fund', methods=['GET', 'POST'])
@login_required
def fund_project(project_id):
    if not current_user.is_funder():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if the project is in funding status
    if project.status != PROJECT_STATUS['FUNDING']:
        flash('هذا المشروع غير متاح للتمويل حالياً', 'warning')
        return redirect(url_for('main.project_detail', project_id=project.id))
    
    form = FundingForm()
    if form.validate_on_submit():
        # Convert amount to integer (fix the issue with string inputs)
        try:
            amount = int(form.amount.data)
        except ValueError:
            flash('يرجى إدخال مبلغ صحيح', 'danger')
            return render_template('funder/fund_project.html', project=project, form=form)
        
        # Create new funding
        new_funding = Funding(
            amount=amount,
            project_id=project.id,
            user_id=current_user.id,
            date=datetime.utcnow()
        )
        
        # Update project funding
        project.current_funding += amount
        project.calculate_progress()
        
        # If project reached 100%, update its status
        if project.funding_progress >= 100:
            project.status = PROJECT_STATUS['FUNDED']
        
        db.session.add(new_funding)
        
        # Create notification for project owner
        notification = Notification(
            user_id=project.owner_id,
            title='تم تمويل مشروعك',
            content=f'مشروعك "{project.title}" تلقى تمويلاً بقيمة {amount} ريال من {current_user.full_name}',
            notification_type='funding',
            related_id=project.id
        )
        
        db.session.add(notification)
        
        # If project is fully funded, create notifications
        if project.funding_progress >= 100:
            # For project owner
            full_notification = Notification(
                user_id=project.owner_id,
                title='اكتمل تمويل مشروعك',
                content=f'تهانينا! تم اكتمال تمويل مشروعك "{project.title}" بنسبة 100%',
                notification_type='full_funding',
                related_id=project.id
            )
            db.session.add(full_notification)
            
            # For all funders
            funders = db.session.query(Funding.user_id).filter(
                Funding.project_id == project.id,
                Funding.user_id != current_user.id
            ).distinct().all()
            
            for funder_id in funders:
                funder_notification = Notification(
                    user_id=funder_id[0],
                    title='اكتمل تمويل مشروع',
                    content=f'تم اكتمال تمويل مشروع "{project.title}" الذي ساهمت فيه بنسبة 100%',
                    notification_type='full_funding',
                    related_id=project.id
                )
                db.session.add(funder_notification)
        
        db.session.commit()
        
        flash('تم تمويل المشروع بنجاح', 'success')
        return redirect(url_for('funder.my_contributions'))
    
    return render_template('funder/fund_project.html', project=project, form=form)

# My contributions
@funder_bp.route('/contributions')
@login_required
def my_contributions():
    if not current_user.is_funder():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    # Get user's fundings with projects
    fundings = db.session.query(Funding, Project).join(
        Project, Funding.project_id == Project.id
    ).filter(Funding.user_id == current_user.id).order_by(Funding.date.desc()).all()
    
    return render_template('funder/contributions.html', fundings=fundings)

# Watchlist
@funder_bp.route('/watchlist')
@login_required
def watchlist():
    if not current_user.is_funder():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    # Get watchlist items with projects
    watchlist_items = db.session.query(Watchlist, Project).join(
        Project, Watchlist.project_id == Project.id
    ).filter(Watchlist.user_id == current_user.id).order_by(Watchlist.date_added.desc()).all()
    
    return render_template('funder/watchlist.html', watchlist_items=watchlist_items)

# Add project to watchlist
@funder_bp.route('/projects/<int:project_id>/watch', methods=['POST'])
@login_required
def add_to_watchlist(project_id):
    if not current_user.is_funder():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # Check if project is already in watchlist
    existing = Watchlist.query.filter_by(
        user_id=current_user.id,
        project_id=project.id
    ).first()
    
    if existing:
        flash('المشروع موجود بالفعل في قائمة المتابعة', 'info')
    else:
        # Add to watchlist
        watchlist_item = Watchlist(
            user_id=current_user.id,
            project_id=project.id,
            date_added=datetime.utcnow()
        )
        
        db.session.add(watchlist_item)
        db.session.commit()
        
        flash('تمت إضافة المشروع إلى قائمة المتابعة', 'success')
    
    # Redirect back to referer or project detail
    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)
    return redirect(url_for('main.project_detail', project_id=project.id))

# Remove project from watchlist
@funder_bp.route('/watchlist/<int:project_id>/remove', methods=['POST'])
@login_required
def remove_from_watchlist(project_id):
    if not current_user.is_funder():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    # Find watchlist item
    watchlist_item = Watchlist.query.filter_by(
        user_id=current_user.id,
        project_id=project_id
    ).first_or_404()
    
    db.session.delete(watchlist_item)
    db.session.commit()
    
    flash('تمت إزالة المشروع من قائمة المتابعة', 'success')
    
    # Redirect back to referer or watchlist
    referer = request.headers.get('Referer')
    if referer and 'watchlist' in referer:
        return redirect(referer)
    return redirect(url_for('funder.watchlist'))

# Explore projects
@funder_bp.route('/explore')
@login_required
def explore():
    if not current_user.is_funder():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    # Get filter parameters
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort_by', 'progress')
    
    # Base query
    query = Project.query.filter_by(status=PROJECT_STATUS['FUNDING'])
    
    # Apply category filter
    if category != 'all':
        query = query.filter_by(category=category)
    
    # Apply sorting
    if sort_by == 'progress':
        query = query.order_by(Project.funding_progress.desc())
    elif sort_by == 'newest':
        query = query.order_by(Project.funding_start_date.desc())
    elif sort_by == 'ending_soon':  # Fixed the missing equal sign
        query = query.order_by(Project.funding_end_date.asc())
    
    projects = query.all()
    
    # Get user's watchlist project IDs
    watchlist_project_ids = [item.project_id for item in Watchlist.query.filter_by(user_id=current_user.id).all()]
    
    return render_template(
        'funder/explore.html',
        projects=projects,
        category=category,
        sort_by=sort_by,
        watchlist_project_ids=watchlist_project_ids
    )

# Edit user profile
@funder_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_funder():
        flash('غير مصرح بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))
    
    form = ProfileForm()
    if form.validate_on_submit():
        # Handle profile image upload
        if form.profile_image.data:
            from routes.project_owner import save_file
            image_path = save_file(form.profile_image.data, 'profiles')
            current_user.profile_image = image_path
        
        # Update user details
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        
        db.session.commit()
        
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('funder.profile'))
    
    # Pre-fill form with existing data
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email
    
    return render_template('funder/profile.html', form=form)