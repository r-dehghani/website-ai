"""
API routes for the personal website.
These routes provide JSON API endpoints for frontend JavaScript interaction.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import desc

from database.models import db, User, Article, Category, Tag, Comment, Setting, Media
from authentication.auth import verify_token, generate_token, has_permission
from utils.validators import (
    validate_email, validate_password, validate_title, 
    validate_content, validate_comment, sanitize_html
)

api = Blueprint('api', __name__)

# Authentication middleware for API routes
@api.before_request
def auth_middleware():
    """Authenticate requests to protected API endpoints."""
    # Public endpoints that don't require authentication
    public_endpoints = [
        '/api/auth/login',
        '/api/auth/register',
        '/api/auth/forgot-password',
        '/api/auth/reset-password',
        '/api/auth/verify-token',
        '/api/articles',
        '/api/articles/'
    ]
    
    # Skip authentication for public endpoints
    for endpoint in public_endpoints:
        if request.path.startswith(endpoint) and request.method == 'GET':
            return
    
    # Check for auth token in headers
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authentication required'}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    # Get user and attach to request
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    # Attach user to request for access in route handlers
    request.user = user

# Error handling
@api.errorhandler(400)
def bad_request(e):
    return jsonify({'error': str(e)}), 400

@api.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Permission denied'}), 403

@api.errorhandler(500)
def server_error(e):
    current_app.logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Server error'}), 500

# Authentication endpoints
@api.route('/auth/login', methods=['POST'])
def login():
    """API endpoint for user login."""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validate inputs
    if not validate_email(email) or not password:
        return jsonify({'error': 'Invalid email or password'}), 400
    
    # Check user credentials
    user = User.query.filter_by(email=email).first()
    
    from werkzeug.security import check_password_hash
    if user and check_password_hash(user.password, password):
        if not user.is_active:
            return jsonify({'error': 'Your account has been deactivated'}), 403
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'avatar': user.avatar
            },
            'token': token
        })
    
    return jsonify({'error': 'Invalid email or password'}), 401

@api.route('/auth/register', methods=['POST'])
def register():
    """API endpoint for user registration."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validate inputs
    errors = []
    if not name or len(name) < 2:
        errors.append('Please enter a valid name')
    
    if not validate_email(email):
        errors.append('Please enter a valid email address')
    elif User.query.filter_by(email=email).first():
        errors.append('Email address already in use')
    
    if not validate_password(password):
        errors.append('Password must be at least 8 characters and include a number and special character')
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Create new user
    from werkzeug.security import generate_password_hash
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role='viewer',  # Default role
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        token = generate_token(new_user.id)
        
        return jsonify({
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role,
                'avatar': new_user.avatar
            },
            'token': token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"User registration error: {str(e)}")
        return jsonify({'error': 'An error occurred during registration'}), 500

# User endpoints
@api.route('/user', methods=['GET'])
def get_current_user():
    """Get current user information."""
    user = request.user
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'bio': user.bio,
        'avatar': user.avatar,
        'website': user.website,
        'twitter': user.twitter,
        'linkedin': user.linkedin,
        'github': user.github,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None
    })

@api.route('/user/profile', methods=['PUT'])
def update_profile():
    """Update user profile."""
    user = request.user
    data = request.get_json()
    
    # Update user details
    user.name = data.get('name', user.name)
    user.bio = data.get('bio', user.bio)
    user.website = data.get('website', user.website)
    user.twitter = data.get('twitter', user.twitter)
    user.linkedin = data.get('linkedin', user.linkedin)
    user.github = data.get('github', user.github)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'An error occurred updating your profile'}), 500

@api.route('/user/password', methods=['PUT'])
def update_password():
    """Update user password."""
    user = request.user
    data = request.get_json()
    
    current_password = data.get('current_password', '')
    new_password = data.get('password', '')
    
    # Validate current password
    from werkzeug.security import check_password_hash, generate_password_hash
    if not check_password_hash(user.password, current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Validate new password
    if not validate_password(new_password):
        return jsonify({'error': 'New password must be at least 8 characters and include a number and special character'}), 400
    
    # Update password
    user.password = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password updated successfully'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password update error: {str(e)}")
        return jsonify({'error': 'An error occurred updating your password'}), 500

# Article endpoints
@api.route('/articles', methods=['GET'])
def get_articles():
    """Get articles with optional filtering and pagination."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    tag = request.args.get('tag')
    search = request.args.get('search')
    status = request.args.get('status', 'published')
    
    # Build the base query
    query = Article.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if category:
        category_obj = Category.query.filter_by(slug=category).first()
        if category_obj:
            query = query.filter_by(category_id=category_obj.id)
    
    if tag:
        tag_obj = Tag.query.filter_by(slug=tag).first()
        if tag_obj:
            query = query.filter(Article.tags.contains(tag_obj))
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Article.title.ilike(search_term) | 
            Article.content.ilike(search_term) | 
            Article.excerpt.ilike(search_term)
        )
    
    # Order by publication date (newest first)
    query = query.order_by(desc(Article.published_at))
    
    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page)
    
    # Convert to JSON response
    articles = [{
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'excerpt': article.excerpt,
        'featured_image': article.featured_image,
        'status': article.status,
        'views': article.views,
        'read_time': article.read_time,
        'published_at': article.published_at.isoformat() if article.published_at else None,
        'category': article.category.name if article.category else None,
        'author': {
            'id': article.author.id,
            'name': article.author.name,
            'avatar': article.author.avatar
        }
    } for article in pagination.items]
    
    return jsonify({
        'articles': articles,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total
        }
    })

@api.route('/articles/<string:slug>', methods=['GET'])
def get_article(slug):
    """Get a single article by slug."""
    article = Article.query.filter_by(slug=slug).first()
    
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    # Check if article is published or user has permission to view drafts
    if article.status != 'published' and (
        not hasattr(request, 'user') or 
        (request.user.id != article.author_id and request.user.role != 'admin')
    ):
        return jsonify({'error': 'Article not found'}), 404
    
    # Increment view count
    article.views += 1
    db.session.commit()
    
    # Get article tags
    tags = [{'id': tag.id, 'name': tag.name, 'slug': tag.slug} for tag in article.tags]
    
    # Convert to JSON response
    article_data = {
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'content': article.content,
        'excerpt': article.excerpt,
        'featured_image': article.featured_image,
        'image_caption': article.image_caption,
        'status': article.status,
        'is_featured': article.is_featured,
        'views': article.views,
        'read_time': article.read_time,
        'published_at': article.published_at.isoformat() if article.published_at else None,
        'created_at': article.created_at.isoformat() if article.created_at else None,
        'updated_at': article.updated_at.isoformat() if article.updated_at else None,
        'category': {
            'id': article.category.id,
            'name': article.category.name,
            'slug': article.category.slug
        } if article.category else None,
        'author': {
            'id': article.author.id,
            'name': article.author.name,
            'avatar': article.author.avatar,
            'bio': article.author.bio
        },
        'tags': tags
    }
    
    return jsonify(article_data)

@api.route('/articles', methods=['POST'])
def create_article():
    """Create a new article."""
    # Check if user is admin or contributor
    if not has_permission('can_create_articles'):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    excerpt = data.get('excerpt', '').strip()
    category_id = data.get('category_id')
    status = data.get('status', 'draft')
    is_featured = data.get('is_featured', False)
    tags = data.get('tags', [])
    
    # Validate inputs
    errors = []
    if not validate_title(title):
        errors.append('Please enter a valid title (3-200 characters)')
    
    if not validate_content(content):
        errors.append('Please enter valid content (at least 10 characters)')
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Create new article
    new_article = Article(
        title=title,
        content=sanitize_html(content),
        excerpt=excerpt or content[:200] + '...',
        author_id=request.user.id,
        category_id=category_id,
        status=status,
        is_featured=is_featured,
        created_at=datetime.utcnow()
    )
    
    # Set publication date if status is published
    if status == 'published':
        new_article.published_at = datetime.utcnow()
    
    try:
        db.session.add(new_article)
        db.session.flush()  # Get the article ID without committing
        
        # Add tags
        for tag_id in tags:
            tag = Tag.query.get(tag_id)
            if tag:
                new_article.tags.append(tag)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Article created successfully',
            'article_id': new_article.id,
            'slug': new_article.slug
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Article creation error: {str(e)}")
        return jsonify({'error': 'An error occurred creating the article'}), 500

@api.route('/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """Update an existing article."""
    article = Article.query.get_or_404(article_id)
    
    # Check if user has permission to edit this article
    if request.user.role != 'admin' and request.user.id != article.author_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    title = data.get('title', article.title).strip()
    content = data.get('content', article.content).strip()
    excerpt = data.get('excerpt', article.excerpt).strip()
    category_id = data.get('category_id', article.category_id)
    status = data.get('status', article.status)
    is_featured = data.get('is_featured', article.is_featured)
    tags = data.get('tags', [])
    
    # Validate inputs
    errors = []
    if not validate_title(title):
        errors.append('Please enter a valid title (3-200 characters)')
    
    if not validate_content(content):
        errors.append('Please enter valid content (at least 10 characters)')
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Update article details
    article.title = title
    article.content = sanitize_html(content)
    article.excerpt = excerpt or content[:200] + '...'
    article.category_id = category_id
    article.status = status
    article.is_featured = is_featured
    
    # Update publication date if status changed to published
    if status == 'published' and article.status != 'published':
        article.published_at = datetime.utcnow()
    
    # Update tags
    article.tags = []
    for tag_id in tags:
        tag = Tag.query.get(tag_id)
        if tag:
            article.tags.append(tag)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Article updated successfully',
            'article_id': article.id,
            'slug': article.slug
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Article update error: {str(e)}")
        return jsonify({'error': 'An error occurred updating the article'}), 500

@api.route('/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """Delete an article."""
    article = Article.query.get_or_404(article_id)
    
    # Check if user has permission to delete this article
    can_delete = request.user.role == 'admin' or (
        request.user.id == article.author_id and has_permission('can_delete_own_articles')
    )
    
    if not can_delete:
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({'message': 'Article deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Article deletion error: {str(e)}")
        return jsonify({'error': 'An error occurred deleting the article'}), 500

@api.route('/articles/draft', methods=['POST'])
def save_draft():
    """Save article as draft."""
    # Check if user is admin or contributor
    if not has_permission('can_create_articles'):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    article_id = data.get('article_id')
    
    # If article_id is provided, update existing draft
    if article_id:
        article = Article.query.get_or_404(article_id)
        
        # Check if user has permission to edit this article
        if request.user.role != 'admin' and request.user.id != article.author_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # Update draft
        if title:
            article.title = title
        if content:
            article.content = sanitize_html(content)
        
        try:
            db.session.commit()
            
            return jsonify({
                'message': 'Draft updated successfully',
                'article_id': article.id
            })
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Draft update error: {str(e)}")
            return jsonify({'error': 'An error occurred updating the draft'}), 500
    
    # Create new draft
    else:
        # Title is required for a new draft
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        new_draft = Article(
            title=title,
            content=sanitize_html(content) if content else '',
            author_id=request.user.id,
            status='draft',
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(new_draft)
            db.session.commit()
            
            return jsonify({
                'message': 'Draft saved successfully',
                'article_id': new_draft.id
            }), 201
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Draft creation error: {str(e)}")
            return jsonify({'error': 'An error occurred saving the draft'}), 500

@api.route('/articles/<int:article_id>/publish', methods=['PUT'])
def publish_article(article_id):
    """Publish a draft article."""
    article = Article.query.get_or_404(article_id)
    
    # Check if user has permission to publish this article
    if request.user.role != 'admin' and request.user.id != article.author_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # Check if article is in draft status
    if article.status != 'draft':
        return jsonify({'error': 'Article is already published'}), 400
    
    # Update article status to published
    article.status = 'published'
    article.published_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Article published successfully',
            'article_id': article.id,
            'slug': article.slug
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Article publishing error: {str(e)}")
        return jsonify({'error': 'An error occurred publishing the article'}), 500

# Comment endpoints
@api.route('/articles/<string:slug>/comments', methods=['GET'])
def get_comments(slug):
    """Get comments for an article."""
    article = Article.query.filter_by(slug=slug).first_or_404()
    
    # Get query parameters for pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Query comments
    query = Comment.query.filter_by(
        article_id=article.id,
        parent_id=None,  # Only get top-level comments
        is_approved=True  # Only get approved comments
    ).order_by(Comment.created_at)
    
    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page)
    
    # Convert to JSON response with replies
    comments = []
    for comment in pagination.items:
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'user': {
                'id': comment.user.id,
                'name': comment.user.name,
                'avatar': comment.user.avatar
            },
            'replies': []
        }
        
        # Get replies for this comment
        replies = Comment.query.filter_by(
            parent_id=comment.id,
            is_approved=True
        ).order_by(Comment.created_at).all()
        
        for reply in replies:
            reply_data = {
                'id': reply.id,
                'content': reply.content,
                'created_at': reply.created_at.isoformat(),
                'user': {
                    'id': reply.user.id,
                    'name': reply.user.name,
                    'avatar': reply.user.avatar
                }
            }
            comment_data['replies'].append(reply_data)
        
        comments.append(comment_data)
    
    return jsonify({
        'comments': comments,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total
        }
    })

@api.route('/articles/<string:slug>/comments', methods=['POST'])
def add_comment(slug):
    """Add a comment to an article."""
    article = Article.query.filter_by(slug=slug).first_or_404()
    
    data = request.get_json()
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')
    
    # Validate input
    if not validate_comment(content):
        return jsonify({'error': 'Please enter a valid comment (between 2 and 1000 characters)'}), 400
    
    # Check if parent comment exists if parent_id is provided
    if parent_id:
        parent_comment = Comment.query.get(parent_id)
        if not parent_comment or parent_comment.article_id != article.id:
            return jsonify({'error': 'Invalid parent comment'}), 400
    
    # Create new comment
    new_comment = Comment(
        content=sanitize_html(content),
        user_id=request.user.id,
        article_id=article.id,
        parent_id=parent_id,
        is_approved=True,  # Auto-approve for now
        created_at=datetime.utcnow()
    )
    
    try:
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': {
                'id': new_comment.id,
                'content': new_comment.content,
                'created_at': new_comment.created_at.isoformat(),
                'user': {
                    'id': request.user.id,
                    'name': request.user.name,
                    'avatar': request.user.avatar
                }
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment creation error: {str(e)}")
        return jsonify({'error': 'An error occurred adding your comment'}), 500

@api.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    """Update a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user has permission to edit this comment
    if request.user.id != comment.user_id and request.user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    # Validate input
    if not validate_comment(content):
        return jsonify({'error': 'Please enter a valid comment (between 2 and 1000 characters)'}), 400
    
    # Update comment
    comment.content = sanitize_html(content)
    comment.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Comment updated successfully',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'updated_at': comment.updated_at.isoformat()
            }
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment update error: {str(e)}")
        return jsonify({'error': 'An error occurred updating your comment'}), 500

@api.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user has permission to delete this comment
    if request.user.id != comment.user_id and request.user.role != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comment deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment deletion error: {str(e)}")
        return jsonify({'error': 'An error occurred deleting your comment'}), 500

# Category endpoints
@api.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories."""
    categories = Category.query.order_by(Category.name).all()
    
    category_list = [{
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'description': category.description
    } for category in categories]
    
    return jsonify({'categories': category_list})

# Tag endpoints
@api.route('/tags', methods=['GET'])
def get_tags():
    """Get all tags."""
    tags = Tag.query.order_by(Tag.name).all()
    
    tag_list = [{
        'id': tag.id,
        'name': tag.name,
        'slug': tag.slug
    } for tag in tags]
    
    return jsonify({'tags': tag_list})

# Settings endpoints
@api.route('/settings', methods=['GET'])
def get_settings():
    """Get public website settings."""
    settings = Setting.query.all()
    
    settings_dict = {}
    for setting in settings:
        settings_dict[setting.name] = setting.value
    
    return jsonify({'settings': settings_dict})