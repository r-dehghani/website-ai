"""
Contributor routes for the personal website.
These routes handle contributor panel functionality like creating and managing articles.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from sqlalchemy import desc, func
from werkzeug.utils import secure_filename
import os
import uuid

from database.models import db, Article, Category, Tag, Comment, Media
from authentication.auth import login_required, role_required
from utils.validators import validate_title, validate_content, sanitize_html

contributor = Blueprint('contributor', __name__)

@contributor.route('/dashboard')
@role_required('contributor')
def dashboard():
    """Contributor dashboard with statistics and recent activity."""
    # Get the current user's articles
    user_id = request.user.id
    
    # Count statistics
    published_articles = Article.query.filter_by(
        author_id=user_id,
        status='published'
    ).count()
    
    draft_articles = Article.query.filter_by(
        author_id=user_id,
        status='draft'
    ).count()
    
    # Get total views for user's articles
    total_views = db.session.query(func.sum(Article.views)).filter(
        Article.author_id == user_id
    ).scalar() or 0
    
    # Get total comments on user's articles
    total_comments = Comment.query.join(Article).filter(
        Article.author_id == user_id
    ).count()
    
    # Get recent articles
    recent_articles = Article.query.filter_by(
        author_id=user_id
    ).order_by(desc(Article.created_at)).limit(5).all()
    
    # Get recent comments on user's articles
    recent_comments = Comment.query.join(Article).filter(
        Article.author_id == user_id
    ).order_by(desc(Comment.created_at)).limit(5).all()
    
    return render_template(
        'contributor/dashboard.html',
        stats={
            'published_articles': published_articles,
            'draft_articles': draft_articles,
            'total_views': total_views,
            'total_comments': total_comments
        },
        recent_articles=recent_articles,
        recent_comments=recent_comments
    )

@contributor.route('/articles')
@role_required('contributor')
def articles():
    """Display the contributor's articles."""
    # Get query parameters for filtering and pagination
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build the base query for the current user's articles
    user_id = request.user.id
    query = Article.query.filter_by(author_id=user_id)
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Article.title.ilike(search_term) | 
            Article.content.ilike(search_term)
        )
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Article.created_at))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    articles = pagination.items
    
    return render_template(
        'contributor/articles.html',
        articles=articles,
        pagination=pagination,
        search=search,
        status=status
    )

@contributor.route('/new-article', methods=['GET', 'POST'])
@role_required('contributor')
def new_article():
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
                'contributor/create_post.html',
                categories=categories,
                tags=tags,
                form=request.form
            )
        
        # Create new article
        new_article = Article(
            title=title,
            content=sanitize_html(content),  # Sanitize HTML content
            excerpt=excerpt or content[:200] + '...',
            author_id=request.user.id,
            category_id=category_id,
            featured_image=featured_image,
            status=status,
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
            
            if status == 'published':
                flash('Article published successfully!', 'success')
            else:
                flash('Article saved as draft.', 'success')
            
            return redirect(url_for('contributor.articles'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Article creation error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template(
        'contributor/create_post.html',
        categories=categories,
        tags=tags
    )

@contributor.route('/edit-article/<int:article_id>', methods=['GET', 'POST'])
@role_required('contributor')
def edit_article(article_id):
    """Edit an existing article."""
    # Get the article and check ownership
    article = Article.query.get_or_404(article_id)
    
    if article.author_id != request.user.id:
        abort(403)  # Forbidden if not the article owner
    
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
                'contributor/edit_post.html',
                article=article,
                categories=categories,
                tags=tags,
                form=request.form
            )
        
        # Update article details
        article.title = title
        article.content = sanitize_html(content)  # Sanitize HTML content
        article.excerpt = excerpt or content[:200] + '...'
        article.category_id = category_id
        article.status = status
        
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
            
            if status == 'published':
                flash('Article updated and published!', 'success')
            else:
                flash('Article updated and saved as draft.', 'success')
            
            return redirect(url_for('contributor.articles'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Article update error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template(
        'contributor/edit_post.html',
        article=article,
        categories=categories,
        tags=tags
    )

@contributor.route('/publish-article/<int:article_id>', methods=['POST'])
@role_required('contributor')
def publish_article(article_id):
    """Publish a draft article."""
    # Get the article and check ownership
    article = Article.query.get_or_404(article_id)
    
    if article.author_id != request.user.id:
        abort(403)  # Forbidden if not the article owner
    
    # Check if article is in draft status
    if article.status != 'draft':
        flash('This article is already published.', 'info')
        return redirect(url_for('contributor.articles'))
    
    # Update article status to published
    article.status = 'published'
    article.published_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash('Article published successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Article publishing error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('contributor.articles'))

@contributor.route('/delete-article/<int:article_id>', methods=['POST'])
@role_required('contributor')
def delete_article(article_id):
    """Delete an article."""
    # Get the article and check ownership
    article = Article.query.get_or_404(article_id)
    
    if article.author_id != request.user.id:
        abort(403)  # Forbidden if not the article owner
    
    try:
        db.session.delete(article)
        db.session.commit()
        flash('Article deleted successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Article deletion error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
    
    return redirect(url_for('contributor.articles'))

@contributor.route('/drafts')
@role_required('contributor')
def drafts():
    """Display the contributor's draft articles."""
    # Get the current user's draft articles
    user_id = request.user.id
    
    # Get query parameters for search and pagination
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build the query for draft articles
    query = Article.query.filter_by(
        author_id=user_id,
        status='draft'
    )
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Article.title.ilike(search_term) | 
            Article.content.ilike(search_term)
        )
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Article.created_at))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    drafts = pagination.items
    
    return render_template(
        'contributor/drafts.html',
        drafts=drafts,
        pagination=pagination,
        search=search
    )

@contributor.route('/comments')
@role_required('contributor')
def comments():
    """Display comments on the contributor's articles."""
    # Get the current user's article IDs
    user_id = request.user.id
    article_ids = [article.id for article in Article.query.filter_by(author_id=user_id).all()]
    
    # Handle empty case
    if not article_ids:
        return render_template('contributor/comments.html', comments=[], pagination=None)
    
    # Get query parameters for pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build the query for comments on user's articles
    query = Comment.query.filter(Comment.article_id.in_(article_ids))
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Comment.created_at))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    comments = pagination.items
    
    return render_template(
        'contributor/comments.html',
        comments=comments,
        pagination=pagination
    )

@contributor.route('/profile')
@role_required('contributor')
def profile():
    """Display the contributor's profile."""
    return render_template('contributor/profile.html', user=request.user)

@contributor.route('/upload-image', methods=['POST'])
@role_required('contributor')
def upload_image():
    """Handle image upload for the rich text editor."""
    if 'image' not in request.files:
        return {'success': False, 'message': 'No file provided'}, 400
    
    file = request.files['image']
    
    if not file or not file.filename:
        return {'success': False, 'message': 'No file selected'}, 400
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return {'success': False, 'message': 'Invalid file type'}, 400
    
    try:
        file_path = save_media_file(file, 'image')
        
        return {
            'success': True,
            'file': {
                'url': file_path
            }
        }
    
    except Exception as e:
        current_app.logger.error(f"Image upload error: {str(e)}")
        return {'success': False, 'message': 'Error uploading image'}, 500

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