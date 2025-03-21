"""
Admin routes for the personal website.
These routes handle admin panel functionality like user management, content management, etc.
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from sqlalchemy import desc, func
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

from database.models import db, User, Article, Category, Tag, Comment, Setting, Media, ActivityLog
from authentication.auth import admin_required
from utils.validators import (
    validate_name, validate_email, validate_password, validate_url,
    validate_title, validate_content, sanitize_html
)

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview statistics."""
    # Get counts for dashboard
    user_count = User.query.count()
    article_count = Article.query.count()
    comment_count = Comment.query.count()
    view_count = db.session.query(func.sum(Article.views)).scalar() or 0
    
    # Get new user count for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_user_count = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    # Calculate user growth percentage
    if user_count > 0:
        user_growth = (new_user_count / user_count) * 100
    else:
        user_growth = 0
    
    # Get recent articles
    recent_articles = Article.query.order_by(desc(Article.created_at)).limit(5).all()
    
    # Get recent users
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    
    # Get recent comments
    recent_comments = Comment.query.order_by(desc(Comment.created_at)).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        stats={
            'total_users': user_count,
            'total_articles': article_count,
            'total_comments': comment_count,
            'total_views': view_count,
            'new_users_percent': round(user_growth, 1),
            'articles_change': 0,  # This would be calculated with real data
            'articles_change_percent': 0,  # This would be calculated with real data
            'views_change': 0,  # This would be calculated with real data
            'views_change_percent': 0,  # This would be calculated with real data
            'comments_change': 0,  # This would be calculated with real data
            'comments_change_percent': 0  # This would be calculated with real data
        },
        recent_articles=recent_articles,
        recent_users=recent_users,
        recent_comments=recent_comments
    )

@admin.route('/users')
@admin_required
def users():
    """User management page."""
    # Get query parameters for filtering and pagination
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build the base query
    query = User.query
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            User.name.ilike(search_term) | 
            User.email.ilike(search_term)
        )
    
    if role:
        query = query.filter_by(role=role)
    
    if status:
        is_active = status == 'active'
        query = query.filter_by(is_active=is_active)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(User.created_at))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    users = pagination.items
    
    return render_template(
        'admin/users.html',
        users=users,
        pagination=pagination,
        search=search,
        role=role,
        status=status
    )

@admin.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create a new user."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'viewer')
        is_active = request.form.get('is_active') == 'on'
        
        # Validate inputs
        errors = []
        if not validate_name(name):
            errors.append('Please enter a valid name.')
        
        if not validate_email(email):
            errors.append('Please enter a valid email address.')
        elif User.query.filter_by(email=email).first():
            errors.append('Email address already in use.')
        
        if not validate_password(password):
            errors.append('Password must be at least 8 characters and include a number and special character.')
        
        if role not in ['admin', 'contributor', 'viewer']:
            errors.append('Invalid role selected.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/create_user.html', form=request.form)
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            is_active=is_active,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Log the activity
            log_activity('create', 'user', new_user.id, f'Created user: {email}')
            
            flash('User created successfully!', 'success')
            return redirect(url_for('admin.users'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"User creation error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/create_user.html')

@admin.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit an existing user."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'viewer')
        is_active = request.form.get('is_active') == 'on'
        
        # Validate inputs
        errors = []
        if not validate_name(name):
            errors.append('Please enter a valid name.')
        
        if not validate_email(email):
            errors.append('Please enter a valid email address.')
        elif email != user.email and User.query.filter_by(email=email).first():
            errors.append('Email address already in use.')
        
        if password and not validate_password(password):
            errors.append('Password must be at least 8 characters and include a number and special character.')
        
        if role not in ['admin', 'contributor', 'viewer']:
            errors.append('Invalid role selected.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/edit_user.html', user=user, form=request.form)
        
        # Update user details
        user.name = name
        user.email = email
        user.role = role
        user.is_active = is_active
        
        # Update password if provided
        if password:
            user.password = generate_password_hash(password)
        
        try:
            db.session.commit()
            
            # Log the activity
            log_activity('update', 'user', user.id, f'Updated user: {email}')
            
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"User update error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/edit_user.html', user=user)

@admin.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        # Log the activity
        log_activity('delete', 'user', user.id, f'Deleted user: {user.email}')
        
        db.session.delete(user)
        db.session.commit()
        
        flash('User deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"User deletion error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.users'))

@admin.route('/articles')
@admin_required
def articles():
    """Article management page."""
    # Get query parameters for filtering and pagination
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build the base query
    query = Article.query
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Article.title.ilike(search_term) | 
            Article.content.ilike(search_term)
        )
    
    if category:
        query = query.filter_by(category_id=category)
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Article.created_at))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    articles = pagination.items
    
    # Get all categories for filter dropdown
    categories = Category.query.all()
    
    return render_template(
        'admin/articles.html',
        articles=articles,
        pagination=pagination,
        search=search,
        category=category,
        status=status,
        categories=categories
    )

@admin.route('/articles/create', methods=['GET', 'POST'])
@admin_required
def create_article():
    """Create a new article."""
    # Get all categories and tags for the form
    categories = Category.query.all()
    tags = Tag.query.all()
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        category_id = request.form.get('category_id', type=int)
        status = request.form.get('status', 'draft')
        is_featured = request.form.get('is_featured') == 'on'
        tag_ids = request.form.getlist('tags', type=int)
        
        # Process featured image if uploaded
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                featured_image = save_media_file(file, 'image')
        
        # Validate inputs
        errors = []
        if not validate_title(title):
            errors.append('Please enter a valid title (3-200 characters).')
        
        if not validate_content(content):
            errors.append('Please enter valid content (at least 10 characters).')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'admin/create_article.html',
                categories=categories,
                tags=tags,
                form=request.form
            )
        
        # Create new article
        new_article = Article(
            title=title,
            content=content,
            excerpt=excerpt or content[:200] + '...',
            author_id=request.user.id,
            category_id=category_id,
            featured_image=featured_image,
            status=status,
            is_featured=is_featured,
            created_at=datetime.utcnow()
        )
        
        # Set publication date if status is published
        if status == 'published':
            new_article.published_at = datetime.utcnow()
        
        # Add tags to article
        if tag_ids:
            for tag_id in tag_ids:
                tag = Tag.query.get(tag_id)
                if tag:
                    new_article.tags.append(tag)
        
        try:
            db.session.add(new_article)
            db.session.commit()
            
            # Log the activity
            log_activity('create', 'article', new_article.id, f'Created article: {title}')
            
            flash('Article created successfully!', 'success')
            return redirect(url_for('admin.articles'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Article creation error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template(
        'admin/create_article.html',
        categories=categories,
        tags=tags
    )

@admin.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@admin_required
def edit_article(article_id):
    """Edit an existing article."""
    article = Article.query.get_or_404(article_id)
    
    # Get all categories and tags for the form
    categories = Category.query.all()
    tags = Tag.query.all()
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        category_id = request.form.get('category_id', type=int)
        status = request.form.get('status', 'draft')
        is_featured = request.form.get('is_featured') == 'on'
        tag_ids = request.form.getlist('tags', type=int)
        
        # Process featured image if uploaded
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                featured_image = save_media_file(file, 'image')
                article.featured_image = featured_image
        
        # Validate inputs
        errors = []
        if not validate_title(title):
            errors.append('Please enter a valid title (3-200 characters).')
        
        if not validate_content(content):
            errors.append('Please enter valid content (at least 10 characters).')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'admin/edit_article.html',
                article=article,
                categories=categories,
                tags=tags,
                form=request.form
            )
        
        # Update article details
        article.title = title
        article.content = content
        article.excerpt = excerpt or content[:200] + '...'
        article.category_id = category_id
        article.status = status
        article.is_featured = is_featured
        
        # Update publication date if status changed to published
        if status == 'published' and article.status != 'published':
            article.published_at = datetime.utcnow()
        
        # Update tags
        article.tags = []
        if tag_ids:
            for tag_id in tag_ids:
                tag = Tag.query.get(tag_id)
                if tag:
                    article.tags.append(tag)
        
        try:
            db.session.commit()
            
            # Log the activity
            log_activity('update', 'article', article.id, f'Updated article: {title}')
            
            flash('Article updated successfully!', 'success')
            return redirect(url_for('admin.articles'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Article update error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template(
        'admin/edit_article.html',
        article=article,
        categories=categories,
        tags=tags
    )

@admin.route('/articles/delete/<int:article_id>', methods=['POST'])
@admin_required
def delete_article(article_id):
    """Delete an article."""
    article = Article.query.get_or_404(article_id)
    
    try:
        # Log the activity
        log_activity('delete', 'article', article.id, f'Deleted article: {article.title}')
        
        db.session.delete(article)
        db.session.commit()
        
        flash('Article deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Article deletion error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.articles'))

@admin.route('/categories')
@admin_required
def categories():
    """Category management page."""
    # Get all categories
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('admin/categories.html', categories=categories)

@admin.route('/categories/create', methods=['GET', 'POST'])
@admin_required
def create_category():
    """Create a new category."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate inputs
        if not name or len(name) < 2 or len(name) > 50:
            flash('Please enter a valid category name (2-50 characters).', 'danger')
            return render_template('admin/create_category.html', form=request.form)
        
        # Check if category already exists
        if Category.query.filter_by(name=name).first():
            flash('A category with this name already exists.', 'danger')
            return render_template('admin/create_category.html', form=request.form)
        
        # Create new category
        new_category = Category(
            name=name,
            description=description
        )
        
        try:
            db.session.add(new_category)
            db.session.commit()
            
            # Log the activity
            log_activity('create', 'category', new_category.id, f'Created category: {name}')
            
            flash('Category created successfully!', 'success')
            return redirect(url_for('admin.categories'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Category creation error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/create_category.html')

@admin.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """Edit an existing category."""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate inputs
        if not name or len(name) < 2 or len(name) > 50:
            flash('Please enter a valid category name (2-50 characters).', 'danger')
            return render_template('admin/edit_category.html', category=category, form=request.form)
        
        # Check if category name already exists (excluding this category)
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category and existing_category.id != category.id:
            flash('A category with this name already exists.', 'danger')
            return render_template('admin/edit_category.html', category=category, form=request.form)
        
        # Update category details
        category.name = name
        category.description = description
        
        try:
            db.session.commit()
            
            # Log the activity
            log_activity('update', 'category', category.id, f'Updated category: {name}')
            
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin.categories'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Category update error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('admin/edit_category.html', category=category)

@admin.route('/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    """Delete a category."""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has articles
    if category.articles:
        flash('Cannot delete category with associated articles.', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        # Log the activity
        log_activity('delete', 'category', category.id, f'Deleted category: {category.name}')
        
        db.session.delete(category)
        db.session.commit()
        
        flash('Category deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Category deletion error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/comments')
@admin_required
def comments():
    """Comment management page."""
    # Get query parameters for filtering and pagination
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build the base query
    query = Comment.query
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(Comment.content.ilike(search_term))
    
    if status:
        is_approved = status == 'approved'
        query = query.filter_by(is_approved=is_approved)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Comment.created_at))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    comments = pagination.items
    
    return render_template(
        'admin/comments.html',
        comments=comments,
        pagination=pagination,
        search=search,
        status=status
    )

@admin.route('/comments/approve/<int:comment_id>', methods=['POST'])
@admin_required
def approve_comment(comment_id):
    """Approve a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    comment.is_approved = True
    
    try:
        db.session.commit()
        
        # Log the activity
        log_activity('update', 'comment', comment.id, f'Approved comment ID: {comment.id}')
        
        flash('Comment approved successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment approval error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.comments'))

@admin.route('/comments/unapprove/<int:comment_id>', methods=['POST'])
@admin_required
def unapprove_comment(comment_id):
    """Unapprove a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    comment.is_approved = False
    
    try:
        db.session.commit()
        
        # Log the activity
        log_activity('update', 'comment', comment.id, f'Unapproved comment ID: {comment.id}')
        
        flash('Comment unapproved successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment unapproval error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.comments'))

@admin.route('/comments/delete/<int:comment_id>', methods=['POST'])
@admin_required
def delete_comment(comment_id):
    """Delete a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        # Log the activity
        log_activity('delete', 'comment', comment.id, f'Deleted comment ID: {comment.id}')
        
        db.session.delete(comment)
        db.session.commit()
        
        flash('Comment deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment deletion error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('admin.comments'))

@admin.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """Website settings management."""
    if request.method == 'POST':
        # Get all settings
        settings = Setting.query.all()
        
        # Update settings with form values
        for setting in settings:
            new_value = request.form.get(setting.name, '')
            if new_value != setting.value:
                setting.value = new_value
        
        try:
            db.session.commit()
            
            # Log the activity
            log_activity('update', 'settings', 0, 'Updated website settings')
            
            flash('Settings updated successfully!', 'success')
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Settings update error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    # Get all settings
    settings = Setting.query.all()
    
    return render_template('admin/settings.html', settings=settings)

# Helper functions

def save_media_file(file, file_type):
    """Save uploaded file and return the file path."""
    # Generate a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Create directory if it doesn't exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(os.path.join(current_app.root_path, upload_folder), exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(os.path.join(current_app.root_path, file_path))
    
    # Create media record
    media = Media(
        filename=filename,
        file_path=f"/{file_path}",
        file_type=file_type,
        file_size=os.path.getsize(os.path.join(current_app.root_path, file_path)),
        user_id=request.user.id,
        uploaded_at=datetime.utcnow()
    )
    
    db.session.add(media)
    
    return f"/{file_path}"

def log_activity(action, entity_type, entity_id, description):
    """Log admin activity."""
    log = ActivityLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        user_id=request.user.id if hasattr(request, 'user') else None,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        created_at=datetime.utcnow()
    )
    
    db.session.add(log)
    db.session.commit()