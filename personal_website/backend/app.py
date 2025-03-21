"""
Main application entry point for the personal website.
Initializes and configures the Flask application.
"""

import os
from flask import Flask, render_template, session, g
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect

from database.models import db, User
from routes.public_routes import public
from routes.admin_routes import admin
from routes.contributor_routes import contributor
from routes.auth_routes import auth_routes
from routes.api_routes import api
from config import config_by_name

# Initialize extensions
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_name='development'):
    """
    Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration environment (development, production, testing)
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__,
                static_folder='../frontend/static',
                template_folder='../frontend/templates')
    
    # Load configuration based on environment
    app.config.from_object(config_by_name[config_name])
    
    # Handle proxies (needed for production behind reverse proxy)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Register blueprints
    app.register_blueprint(public)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(contributor, url_prefix='/contributor')
    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')
    
    # Global context processor for templates
    @app.context_processor
    def inject_global_vars():
        return {
            'current_user': g.user if hasattr(g, 'user') else None
        }
    
    # Request hooks
    @app.before_request
    def load_user():
        """Load user from session if available."""
        user_id = session.get('user_id')
        if user_id:
            g.user = User.query.get(user_id)
        else:
            g.user = None
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.cli.command("init-db")
    def init_db():
        """Initialize database with basic data."""
        from database.schema import init_database
        init_database(app)
        print("Database initialized with sample data.")
    
    @app.cli.command("create-admin")
    def create_admin():
        """Create admin user."""
        from werkzeug.security import generate_password_hash
        from database.models import User
        
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
        
        admin = User.query.filter_by(email=admin_email).first()
        if admin:
            print(f"Admin user {admin_email} already exists.")
            return
        
        new_admin = User(
            name='Administrator',
            email=admin_email,
            password=generate_password_hash(admin_password),
            role='admin',
            is_active=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user created with email: {admin_email}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)