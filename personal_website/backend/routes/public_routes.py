"""
Public routes for the personal website.
These routes handle publicly accessible pages like the homepage, about page, articles, etc.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from sqlalchemy import desc
from database.models import db, Article, Category, Tag, Comment, User, Setting
from utils.validators import validate_comment, sanitize_html
from authentication.auth import login_required, has_permission

public = Blueprint('public', __name__)

def get_settings():
    """Get website settings from database."""
    settings = {}
    for setting in Setting.query.all():
        settings[setting.name] = setting.value
    return settings

@public.route('/')
def index():
    """Handle the homepage."""
    # Get site settings
    settings = get_settings()
    
    # Get featured articles
    featured_articles = Article.query.filter_by(
        status='published',
        is_featured=True
    ).order_by(desc(Article.published_at)).limit(3).all()
    
    # Get latest articles
    latest_articles = Article.query.filter_by(
        status='published'
    ).order_by(desc(Article.published_at)).limit(6).all()
    
    # Get categories
    categories = Category.query.all()
    
    return render_template(
        'public/index.html',
        settings=settings,
        featured_articles=featured_articles,
        latest_articles=latest_articles,
        categories=categories
    )

@public.route('/about')
def about():
    """Handle the about page."""
    # Get site settings
    settings = get_settings()
    
    # Get admin user for about page
    admin = User.query.filter_by(role='admin').first()
    
    return render_template(
        'public/about.html',
        settings=settings,
        admin=admin
    )

@public.route('/contact', methods=['GET', 'POST'])
def contact():
    """Handle the contact page and form submission."""
    # Get site settings
    settings = get_settings()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate inputs
        errors = []
        if not name or len(name) < 2:
            errors.append('Please enter your name')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address')
        
        if not subject or len(subject) < 3:
            errors.append('Please enter a subject')
        
        if not message or len(message) < 10:
            errors.append('Please enter a message (minimum 10 characters)')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'public/contact.html',
                settings=settings,
                form=request.form
            )
        
        # In a real application, send the email here
        # For now, just simulate success
        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('public.contact'))
    
    return render_template(
        'public/contact.html',
        settings=settings
    )

@public.route('/articles')
def articles():
    """Handle the articles listing page."""
    # Get site settings
    settings = get_settings()
    
    # Get query parameters for filtering
    category_slug = request.args.get('category')
    tag_slug = request.args.get('tag')
    search_query = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = int(settings.get('posts_per_page', 10))
    
    # Build the base query
    query = Article.query.filter_by(status='published')
    
    # Apply filters if provided
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)
    
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
        query = query.filter(Article.tags.contains(tag))
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            Article.title.ilike(search) | 
            Article.content.ilike(search) | 
            Article.excerpt.ilike(search)
        )
    
    # Order by publication date (newest first)
    query = query.order_by(desc(Article.published_at))
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    articles = pagination.items
    
    # Get all categories for filter dropdown
    categories = Category.query.all()
    
    return render_template(
        'public/blog.html',
        settings=settings,
        articles=articles,
        pagination=pagination,
        categories=categories,
        current_category=category_slug,
        current_tag=tag_slug,
        search_query=search_query
    )

@public.route('/articles/<string:slug>')
def article_detail(slug):
    """Handle individual article display."""
    # Get site settings
    settings = get_settings()
    
    # Get the article by slug
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Increment view count
    article.views += 1
    db.session.commit()
    
    # Get article comments
    enable_comments = settings.get('enable_comments', 'true') == 'true'
    moderated_comments = settings.get('moderated_comments', 'false') == 'true'
    
    if enable_comments:
        # If moderation is enabled, only show approved comments
        if moderated_comments:
            comments = Comment.query.filter_by(
                article_id=article.id,
                is_approved=True,
                parent_id=None  # Only get top-level comments
            ).order_by(Comment.created_at).all()
        else:
            comments = Comment.query.filter_by(
                article_id=article.id,
                parent_id=None  # Only get top-level comments
            ).order_by(Comment.created_at).all()
    else:
        comments = []
    
    # Get related articles (same category or tags)
    related_articles = []
    
    if article.category:
        # Get articles from the same category
        category_articles = Article.query.filter(
            Article.category_id == article.category_id,
            Article.id != article.id,
            Article.status == 'published'
        ).order_by(desc(Article.published_at)).limit(3).all()
        
        related_articles.extend(category_articles)
    
    # If we need more related articles, get ones with the same tags
    if len(related_articles) < 3 and article.tags:
        # Get article IDs that we already have
        existing_ids = [a.id for a in related_articles]
        existing_ids.append(article.id)
        
        # Get articles with any of the same tags
        for tag in article.tags:
            tag_articles = Article.query.filter(
                Article.tags.contains(tag),
                ~Article.id.in_(existing_ids),
                Article.status == 'published'
            ).order_by(desc(Article.published_at)).limit(3 - len(related_articles)).all()
            
            related_articles.extend(tag_articles)
            
            # Break if we have enough related articles
            if len(related_articles) >= 3:
                break
    
    return render_template(
        'public/blog_post.html',
        settings=settings,
        article=article,
        comments=comments,
        related_articles=related_articles,
        enable_comments=enable_comments
    )

@public.route('/articles/<string:slug>/comment', methods=['POST'])
@login_required
def add_comment(slug):
    """Handle comment submission on an article."""
    # Get site settings
    settings = get_settings()
    
    # Check if comments are enabled
    enable_comments = settings.get('enable_comments', 'true') == 'true'
    if not enable_comments:
        flash('Comments are currently disabled.', 'danger')
        return redirect(url_for('public.article_detail', slug=slug))
    
    # Get the article
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Get comment data
    comment_content = request.form.get('comment', '').strip()
    parent_id = request.form.get('parent_id', None, type=int)
    
    # Validate comment
    if not validate_comment(comment_content):
        flash('Please enter a valid comment (between 2 and 1000 characters).', 'danger')
        return redirect(url_for('public.article_detail', slug=slug))
    
    # Sanitize HTML content if any
    comment_content = sanitize_html(comment_content)
    
    # Check if comment moderation is enabled
    moderated_comments = settings.get('moderated_comments', 'false') == 'true'
    
    # Create the comment
    comment = Comment(
        content=comment_content,
        user_id=request.user.id,
        article_id=article.id,
        parent_id=parent_id,
        is_approved=not moderated_comments,  # Auto-approve if moderation is off
        created_at=datetime.utcnow()
    )
    
    db.session.add(comment)
    db.session.commit()
    
    if moderated_comments:
        flash('Your comment has been submitted and is awaiting approval.', 'info')
    else:
        flash('Your comment has been added successfully.', 'success')
    
    return redirect(url_for('public.article_detail', slug=slug))

@public.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Handle comment deletion."""
    # Get the comment
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the user is authorized to delete the comment
    if comment.user_id != request.user.id and not has_permission('can_delete_any_comment'):
        abort(403)
    
    # Get the article for redirect
    article = Article.query.get_or_404(comment.article_id)
    
    # Delete the comment
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully.', 'success')
    
    return redirect(url_for('public.article_detail', slug=article.slug))