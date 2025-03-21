"""
Helper functions for the personal website.
Contains utility functions used throughout the application.
"""

import datetime
from flask import current_app
from slugify import slugify
import uuid
import os
import re
from database.models import Setting, db

def get_settings():
    """
    Get all website settings from the database.
    
    Returns:
        dict: Dictionary of settings (name: value)
    """
    settings = {}
    for setting in Setting.query.all():
        settings[setting.name] = setting.value
    return settings

def format_date(date, format_string='%B %d, %Y'):
    """
    Format a datetime object as a string.
    
    Args:
        date (datetime): The datetime to format
        format_string (str): The format string to use
        
    Returns:
        str: Formatted date string
    """
    if not date:
        return ''
    
    return date.strftime(format_string)

def get_read_time(content, words_per_minute=200):
    """
    Calculate reading time for content.
    
    Args:
        content (str): The content to calculate reading time for
        words_per_minute (int): Reading speed in words per minute
        
    Returns:
        int: Reading time in minutes
    """
    if not content:
        return 1
    
    # Count words in content (strip HTML tags first)
    clean_text = re.sub(r'<[^>]+>', '', content)
    word_count = len(clean_text.split())
    
    # Calculate reading time
    minutes = max(1, word_count // words_per_minute)
    
    return minutes

def generate_slug(title, model=None, model_id=None):
    """
    Generate a URL-friendly slug from a title.
    
    Args:
        title (str): The title to generate a slug from
        model: The model class to check for existing slugs
        model_id: The ID of the model being updated (to avoid conflicts with itself)
        
    Returns:
        str: A unique slug
    """
    if not title:
        return str(uuid.uuid4())
    
    # Generate base slug
    base_slug = slugify(title)
    
    # If no model provided, just return the base slug
    if not model:
        return base_slug
    
    # Check if slug exists
    slug = base_slug
    counter = 1
    
    while True:
        # Check if slug exists, excluding the current item if model_id is provided
        if model_id:
            existing = model.query.filter(model.slug == slug, model.id != model_id).first()
        else:
            existing = model.query.filter_by(slug=slug).first()
        
        # If slug doesn't exist, return it
        if not existing:
            return slug
        
        # Otherwise, add a counter and try again
        slug = f"{base_slug}-{counter}"
        counter += 1

def save_file(file, directory):
    """
    Save an uploaded file to the specified directory.
    
    Args:
        file: The file to save
        directory (str): The directory to save to (relative to upload folder)
        
    Returns:
        str: The path to the saved file
    """
    from werkzeug.utils import secure_filename
    
    # Create a secure filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Ensure directory exists
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], directory)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(os.path.join(current_app.root_path, file_path))
    
    # Return the relative path from static directory
    return f"/{file_path}"

def send_email(to, subject, template, **kwargs):
    """
    Send an email.
    
    Args:
        to (str): Recipient email
        subject (str): Email subject
        template (str): Template name
        **kwargs: Template variables
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # In a real application, this would use Flask-Mail to send emails
    # For now, we'll just log the email
    current_app.logger.info(f"Email to: {to}, Subject: {subject}, Template: {template}, Data: {kwargs}")
    return True

def log_activity(user_id, action, entity_type, entity_id, description=None):
    """
    Log a user activity.
    
    Args:
        user_id (int): User ID
        action (str): Action performed
        entity_type (str): Type of entity (user, article, comment, etc.)
        entity_id (int): ID of the entity
        description (str, optional): Additional description
        
    Returns:
        bool: True if logged successfully, False otherwise
    """
    # In a real application, this would log to the activity_logs table
    # For simplicity, we'll just log to the application logger
    current_app.logger.info(
        f"Activity: User {user_id} performed {action} on {entity_type} {entity_id}"
        + (f" - {description}" if description else "")
    )
    return True

def get_client_ip():
    """
    Get the client's IP address.
    
    Returns:
        str: Client IP address
    """
    from flask import request
    
    # Check for X-Forwarded-For header (for proxies)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    else:
        ip = request.remote_addr
    
    return ip

def truncate_text(text, max_length=200, suffix='...'):
    """
    Truncate text to a specified length.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if not text:
        return ''
    
    # Clean HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Truncate if longer than max_length
    if len(clean_text) <= max_length:
        return clean_text
    
    # Find the last space before max_length
    truncated = clean_text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space != -1:
        truncated = truncated[:last_space]
    
    return truncated + suffix