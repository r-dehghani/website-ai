"""
Authentication routes for the personal website.
These routes handle user authentication, registration, and profile management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from database.models import db, User
from authentication.auth import login_required
from utils.validators import validate_email, validate_password, validate_name
import os
from werkzeug.utils import secure_filename
import uuid

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Verify password
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

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms') == 'on'
        
        # Validate inputs
        errors = []
        if not validate_name(name):
            errors.append('Please enter a valid name (at least 2 characters).')
        
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
            return render_template('auth/register.html', form=request.form)
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role='viewer',  # Default role for new users
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            session['user_id'] = new_user.id
            
            flash('Account created successfully! Welcome to the community.', 'success')
            return redirect(url_for('public.index'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html')

@auth_routes.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('user_id', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('public.index'))

@auth_routes.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request."""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/reset_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        # Always show success message even if email doesn't exist (security measure)
        flash('If your email is registered, you will receive password reset instructions.', 'info')
        
        if user:
            # In a real app, generate token and send email
            # For demo purposes, we'll just show a link
            from itsdangerous import URLSafeTimedSerializer
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(email, salt='password-reset')
            reset_url = url_for('auth_routes.reset_password', token=token, _external=True)
            
            # In production, send email with reset link
            # For now, just log it
            current_app.logger.info(f"Password reset link: {reset_url}")
            
            # In development, show the link to the user
            if current_app.debug:
                flash(f"Debug: {reset_url}", 'info')
        
        # Redirect to login page
        return redirect(url_for('auth_routes.login'))
    
    return render_template('auth/reset_password.html')

@auth_routes.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('public.index'))
    
    try:
        # Verify token (expires after 1 hour)
        from itsdangerous import URLSafeTimedSerializer
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid or expired reset link.', 'danger')
            return redirect(url_for('auth_routes.reset_password_request'))
    
    except:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth_routes.reset_password_request'))
    
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
        
        flash('Your password has been updated successfully. You can now log in.', 'success')
        return redirect(url_for('auth_routes.login'))
    
    return render_template('auth/new_password.html', token=token)

@auth_routes.route('/profile', methods=['GET'])
@login_required
def profile():
    """Display user profile."""
    # Get current user from database to ensure we have the latest data
    user = User.query.get(session['user_id'])
    
    if not user:
        session.pop('user_id', None)
        flash('Your account could not be found.', 'danger')
        return redirect(url_for('auth_routes.login'))
    
    return render_template('auth/profile.html', user=user)

@auth_routes.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    user = User.query.get(session['user_id'])
    
    if not user:
        session.pop('user_id', None)
        flash('Your account could not be found.', 'danger')
        return redirect(url_for('auth_routes.login'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        bio = request.form.get('bio', '').strip()
        website = request.form.get('website', '').strip()
        twitter = request.form.get('twitter', '').strip()
        linkedin = request.form.get('linkedin', '').strip()
        github = request.form.get('github', '').strip()
        
        # Validate name
        if not validate_name(name):
            flash('Please enter a valid name (at least 2 characters).', 'danger')
            return render_template('auth/edit_profile.html', user=user)
        
        # Update profile picture if provided
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename:
                # Check file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in avatar.filename and avatar.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # Create a unique filename
                    filename = secure_filename(avatar.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    
                    # Ensure upload directory exists
                    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save the file
                    file_path = os.path.join(upload_dir, unique_filename)
                    avatar.save(os.path.join(current_app.root_path, file_path))
                    
                    # Update user avatar path
                    user.avatar = f"/{file_path}"
                else:
                    flash('Invalid file type. Please upload a PNG, JPG, JPEG, or GIF.', 'danger')
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
            return redirect(url_for('auth_routes.profile'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Profile update error: {str(e)}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    
    return render_template('auth/edit_profile.html', user=user)

@auth_routes.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    user = User.query.get(session['user_id'])
    
    if not user:
        session.pop('user_id', None)
        flash('Your account could not be found.', 'danger')
        return redirect(url_for('auth_routes.login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Verify current password
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        # Validate new password
        if not validate_password(new_password):
            flash('New password must be at least 8 characters and include a number and special character.', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        # Update password
        user.password = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('auth_routes.profile'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Password change error: {str(e)}")
            flash('An error occurred while changing your password. Please try again.', 'danger')
    
    return render_template('auth/change_password.html')