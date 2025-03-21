"""
Input validators for the personal website.
Contains functions to validate user inputs like emails, passwords, etc.
"""

import re
from urllib.parse import urlparse

def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    if not email or len(email) > 100:
        return False
    
    # Regular expression for email validation
    pattern = r'^[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+$'
    return bool(re.match(pattern, email, re.IGNORECASE))

def validate_password(password):
    """
    Validate password strength.
    Password must be at least 8 characters and include a number and special character.
    
    Args:
        password (str): Password to validate
        
    Returns:
        bool: True if password is valid, False otherwise
    """
    if not password or len(password) < 8:
        return False
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_name(name):
    """
    Validate user name.
    
    Args:
        name (str): Name to validate
        
    Returns:
        bool: True if name is valid, False otherwise
    """
    if not name or len(name) < 2 or len(name) > 100:
        return False
    
    # Name should not contain special characters except for spaces, hyphens, and apostrophes
    pattern = r'^[A-Za-z\s\-\']+'
    return bool(re.match(pattern, name))

def validate_username(username):
    """
    Validate username format.
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if username is valid, False otherwise
    """
    if not username or len(username) < 3 or len(username) > 30:
        return False
    
    # Username should only contain alphanumeric characters, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_\-]+'
    return bool(re.match(pattern, username))

def validate_url(url):
    """
    Validate URL format.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url:
        return True  # Empty URL is allowed (considered valid)
    
    if len(url) > 200:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_slug(slug):
    """
    Validate slug format.
    
    Args:
        slug (str): Slug to validate
        
    Returns:
        bool: True if slug is valid, False otherwise
    """
    if not slug or len(slug) < 3 or len(slug) > 100:
        return False
    
    # Slug should only contain lowercase alphanumeric characters and hyphens
    pattern = r'^[a-z0-9\-]+'
    return bool(re.match(pattern, slug))

def validate_title(title):
    """
    Validate article title.
    
    Args:
        title (str): Title to validate
        
    Returns:
        bool: True if title is valid, False otherwise
    """
    if not title or len(title) < 3 or len(title) > 200:
        return False
    
    return True

def validate_content(content):
    """
    Validate article content.
    
    Args:
        content (str): Content to validate
        
    Returns:
        bool: True if content is valid, False otherwise
    """
    if not content or len(content) < 10:
        return False
    
    return True

def validate_comment(comment):
    """
    Validate comment content.
    
    Args:
        comment (str): Comment to validate
        
    Returns:
        bool: True if comment is valid, False otherwise
    """
    if not comment or len(comment) < 2 or len(comment) > 1000:
        return False
    
    return True

def sanitize_html(html_content):
    """
    Sanitize HTML content to remove potentially malicious tags.
    
    Args:
        html_content (str): HTML content to sanitize
        
    Returns:
        str: Sanitized HTML content
    """
    # In a real application, use a library like bleach to sanitize HTML
    # This is a placeholder implementation
    if not html_content:
        return ''
    
    # Strip script and iframe tags (basic sanitization)
    sanitized = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL)
    sanitized = re.sub(r'<iframe.*?>.*?</iframe>', '', sanitized, flags=re.DOTALL)
    
    return sanitized