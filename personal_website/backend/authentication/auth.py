"""
Authentication module for the personal website.
Handles user authentication, registration, and role-based access control.
"""

import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, session, redirect, url_for, render_template, flash, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from itsdangerous import URLSafeTimedSerializer
from database.models import User, db
from utils.validators import validate_email, validate_password, validate_name

# Create Blueprint
auth = Blueprint('auth', __name__)

# Configure serializer for tokens
serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'default-secret-key'))

# User roles and their permissions
ROLES = {
    'viewer': {
        'can_view_articles': True,
        'can_comment': True,
        'can_like': True
    },
    'contributor': {
        'can_view_articles': True,
        'can_comment': True,
        'can_like': True,
        'can_create_articles': True,
        'can_edit_own_articles': True,
        'can_delete_own_articles': True
    },
    'admin': {
        'can_view_articles': True,
        'can_comment': True,
        'can_like': True,
        'can_create_articles': True,
        'can_edit_any_article': True,
        'can_delete_any_article': True,
        'can_manage_users': True,
        'can_manage_settings': True
    }
}

def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to require a specific role for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.headers.get('Content-Type') == 'application/json':
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login', next=request.url))
            
            user = User.query.get(session['user_id'])
            if user.role != role and user.role != 'admin':
                if request.headers.get('Content-Type') == 'application/json':
                    return jsonify({'error': 'Permission denied'}), 403
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('public.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Admin permission required'}), 403
            flash('Admin access required.', 'danger')
            return redirect(url_for('public.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def has_permission(permission):
    """Check if the current user has a specific permission."""
    if 'user_id' not in session:
        return False
    
    user = User.query.get(session['user_id'])
    if not user:
        return False
    
    role_permissions = ROLES.get(user.role, {})
    return role_permissions.get(permission, False)

def generate_token(user_id, expires_in=3600):
    """Generate a JWT token for API authentication."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY', 'default-secret-key'),
        algorithm='HS256'
    )

def verify_token(token):
    """Verify a JWT token and return the user ID."""
    try:
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY', 'default-secret-key'),
            algorithms=['HS256']
        )
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms') == 'on'
        
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
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not terms:
            errors.append('You must agree to the Terms of Service and Privacy Policy.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role='viewer',
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            session['user_id'] = new_user.id
            flash('Account created successfully!', 'success')
            
            # Redirect to intended page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('public.index'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            current_app.logger.error(f"Registration error: {str(e)}")
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html')
            
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Set session
            session['user_id'] = user.id
            
            # Set session expiry for "remember me"
            if remember:
                # Session lasts for 30 days
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=30)
            else:
                # Session expires when browser is closed
                session.permanent = False
            
            flash('Logged in successfully!', 'success')
            
            # Redirect to intended page or dashboard based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'contributor':
                return redirect(url_for('contributor.dashboard'))
            else:
                return redirect(url_for('public.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.index'))

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request."""
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/reset_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        # Always show success message even if email doesn't exist (security measure)
        flash('If your email is registered, you will receive a password reset link.', 'info')
        
        if user:
            # Generate token
            token = serializer.dumps(email, salt='password-reset')
            
            # Create reset link
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # In a real application, send the email here
            print(f"Password reset link for {email}: {reset_url}")
            
            # For testing purposes, we'll flash the URL (remove in production)
            if current_app.debug:
                flash(f"Debug mode: {reset_url}", 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    try:
        # Verify token (expires after 1 hour)
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid or expired reset link.', 'danger')
            return redirect(url_for('auth.reset_password_request'))
    
    except:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not validate_password(password):
            flash('Password must be at least 8 characters and include a number and special character.', 'danger')
            return render_template('auth/new_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/new_password.html', token=token)
        
        # Update password
        user.password = generate_password_hash(password)
        db.session.commit()
        
        flash('Your password has been updated. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/new_password.html', token=token)

@auth.route('/profile', methods=['GET'])
@login_required
def profile():
    """Display user profile."""
    user = User.query.get(session['user_id'])
    return render_template('auth/profile.html', user=user)

@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        bio = request.form.get('bio', '').strip()
        website = request.form.get('website', '').strip()
        twitter = request.form.get('twitter', '').strip()
        linkedin = request.form.get('linkedin', '').strip()
        github = request.form.get('github', '').strip()
        
        if not validate_name(name):
            flash('Please enter a valid name.', 'danger')
            return render_template('auth/edit_profile.html', user=user)
        
        # Update user profile
        user.name = name
        user.bio = bio
        user.website = website
        user.twitter = twitter
        user.linkedin = linkedin
        user.github = github
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            current_app.logger.error(f"Profile update error: {str(e)}")
    
    return render_template('auth/edit_profile.html', user=user)

@auth.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        if not validate_password(new_password):
            flash('New password must be at least 8 characters and include a number and special character.', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Your password has been updated.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')

# API Authentication Endpoints

@auth.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login."""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password, password):
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Your account has been deactivated.'
            }), 403
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'avatar': user.avatar
            }
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid email or password.'
    }), 401

@auth.route('/api/auth/register', methods=['POST'])
def api_register():
    """API endpoint for user registration."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
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
    
    if errors:
        return jsonify({
            'success': False,
            'message': errors[0],
            'errors': errors
        }), 400
    
    # Create new user
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role='viewer',
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        token = generate_token(new_user.id)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role,
                'avatar': new_user.avatar
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"API registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@auth.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    """API endpoint for password reset request."""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not validate_email(email):
        return jsonify({
            'success': False,
            'message': 'Please enter a valid email address.'
        }), 400
    
    user = User.query.filter_by(email=email).first()
    
    # Always show success message even if email doesn't exist (security measure)
    if user:
        # Generate token
        token = serializer.dumps(email, salt='password-reset')
        
        # Create reset link
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        # In a real application, send the email here
        print(f"Password reset link for {email}: {reset_url}")
    
    return jsonify({
        'success': True,
        'message': 'If your email is registered, you will receive a password reset link.'
    })

@auth.route('/api/auth/reset-password', methods=['POST'])
def api_reset_password():
    """API endpoint for password reset with token."""
    data = request.get_json()
    
    token = data.get('token', '')
    password = data.get('password', '')
    
    if not validate_password(password):
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters and include a number and special character.'
        }), 400
    
    try:
        # Verify token (expires after 1 hour)
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired reset link.'
            }), 400
        
        # Update password
        user.password = generate_password_hash(password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Your password has been updated. You can now log in.'
        })
    
    except:
        return jsonify({
            'success': False,
            'message': 'Invalid or expired reset link.'
        }), 400

@auth.route('/api/auth/verify-token', methods=['POST'])
def api_verify_token():
    """API endpoint to verify token validity."""
    data = request.get_json()
    token = data.get('token', '')
    
    user_id = verify_token(token)
    
    if user_id:
        user = User.query.get(user_id)
        
        if user and user.is_active:
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'avatar': user.avatar
                }
            })
    
    return jsonify({
        'success': False,
        'message': 'Invalid or expired token.'
    }), 401