"""
Database models for the personal website.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from slugify import slugify

db = SQLAlchemy()

class User(db.Model):
    """User model representing website users."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='viewer')  # viewer, contributor, admin
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), default='/static/assets/images/avatar-placeholder.jpg')
    website = db.Column(db.String(100), nullable=True)
    twitter = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(100), nullable=True)
    github = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    articles = db.relationship('Article', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'bio': self.bio,
            'avatar': self.avatar,
            'website': self.website,
            'twitter': self.twitter,
            'linkedin': self.linkedin,
            'github': self.github,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Category(db.Model):
    """Category model for classifying articles."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    articles = db.relationship('Article', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        """Convert category object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description
        }

@event.listens_for(Category.name, 'set')
def generate_category_slug(target, value, oldvalue, initiator):
    """Auto-generate slug from name when category is created or updated."""
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value)

class Tag(db.Model):
    """Tag model for labeling articles."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    slug = db.Column(db.String(40), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        """Convert tag object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug
        }

@event.listens_for(Tag.name, 'set')
def generate_tag_slug(target, value, oldvalue, initiator):
    """Auto-generate slug from name when tag is created or updated."""
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value)

# Association table for Article and Tag many-to-many relationship
article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Article(db.Model):
    """Article model representing blog posts."""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    featured_image = db.Column(db.String(200), nullable=True)
    image_caption = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, published
    is_featured = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    read_time = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # Relationships
    tags = db.relationship('Tag', secondary=article_tags, lazy='subquery',
                         backref=db.backref('articles', lazy=True))
    comments = db.relationship('Comment', backref='article', lazy=True)
    
    def __repr__(self):
        return f'<Article {self.title}>'
    
    def to_dict(self):
        """Convert article object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'featured_image': self.featured_image,
            'image_caption': self.image_caption,
            'status': self.status,
            'is_featured': self.is_featured,
            'views': self.views,
            'read_time': self.read_time,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': self.author.to_dict() if self.author else None,
            'category': self.category.to_dict() if self.category else None,
            'tags': [tag.to_dict() for tag in self.tags],
            'comments_count': len(self.comments)
        }

@event.listens_for(Article.title, 'set')
def generate_article_slug(target, value, oldvalue, initiator):
    """Auto-generate slug from title when article is created."""
    if value and not target.slug:
        # Generate base slug from title
        base_slug = slugify(value)
        # Check if slug exists and append timestamp if needed
        if Article.query.filter_by(slug=base_slug).first():
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            target.slug = f"{base_slug}-{timestamp}"
        else:
            target.slug = base_slug

@event.listens_for(Article.content, 'set')
def calculate_read_time(target, value, oldvalue, initiator):
    """Calculate estimated reading time when content is set or updated."""
    if value:
        # Average reading speed: 200 words per minute
        word_count = len(value.split())
        read_minutes = word_count // 200
        # At least 1 minute read time
        target.read_time = max(1, read_minutes)

class Comment(db.Model):
    """Comment model for article comments."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # Relationship for nested comments (replies)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def __repr__(self):
        return f'<Comment {self.id}>'
    
    def to_dict(self):
        """Convert comment object to dictionary."""
        return {
            'id': self.id,
            'content': self.content,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_dict() if self.user else None,
            'article_id': self.article_id,
            'parent_id': self.parent_id,
            'replies_count': self.replies.count()
        }

class Setting(db.Model):
    """Setting model for website configuration."""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Setting {self.name}>'

class Media(db.Model):
    """Media model for uploaded files."""
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # image, document, etc.
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    alt_text = db.Column(db.String(200), nullable=True)
    caption = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship
    user = db.relationship('User', backref='media', lazy=True)
    
    def __repr__(self):
        return f'<Media {self.filename}>'
    
    def to_dict(self):
        """Convert media object to dictionary."""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'alt_text': self.alt_text,
            'caption': self.caption,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'user_id': self.user_id
        }

class ActivityLog(db.Model):
    """Activity log model for tracking user actions."""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # user, article, comment, etc.
    entity_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='activity_logs', lazy=True)
    
    def __repr__(self):
        return f'<ActivityLog {self.action}>'