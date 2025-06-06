
"""
This module initializes and configures the Flask application for the Alumni-Student Engagement System.
Modules and their purposes:
- Flask and Extensions:
    - Initializes the Flask application and configures it using the provided configuration class.
    - Sets up CSRF protection for security.
    - Initializes Flask extensions such as SQLAlchemy (db), Flask-Login (login_manager), Flask-Migrate (migrate), and Flask-Mail (mail).
- Context Processor:
    - Provides a context processor to inject the latest announcement into templates for dynamic rendering.
- Login Manager:
    - Configures the login manager to handle user authentication.
    - Defines a user loader function to retrieve user information from the database.
- Security Headers:
    - (Commented out) Adds security headers such as Content Security Policy (CSP), X-Content-Type-Options, and X-Frame-Options to enhance application security.
- Blueprints:
    - Imports and registers blueprints for modularizing the application.
    - Blueprints include authentication, admin, views, messaging, events, jobs, and main routes.
- CLI Commands:
    - Registers custom CLI commands for managing the application.
- Error Handlers:
    - Defines an error handler for HTTP 403 (Forbidden) errors to render a custom error page.
Returns:
        Flask app instance: The configured Flask application instance.
"""
from flask import Flask, render_template
from config import Config
from .extensions import db, login_manager, migrate, mail
from flask_wtf import CSRFProtect
from flask_mail import Mail, Message
from app.models import Announcement

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.context_processor
    def inject_latest_announcement():
        latest_announcement = Announcement.query.order_by(Announcement.created_at.desc()).first()
        return dict(get_latest_announcement=lambda: latest_announcement)

    csrf = CSRFProtect(app)  # Initialize CSRF protection
    app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for CSRF protection
    csrf.init_app(app)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)


    mail.init_app(app)
    # Initialize the Flask-Mail extension
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Local import to avoid circular dependency
        return User.query.get(int(user_id))
    
    # Security headers
    @app.after_request
    def apply_security_headers(response):

    #     csp_policy = (
    #      "default-src 'self'; "
    # "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
    # "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://embed.tawk.to https://va.tawk.to; "
    # "font-src 'self' data: https://cdn.jsdelivr.net https://fonts.gstatic.com https://fonts.googleapis.com; "
    # "img-src 'self' data: https:; "
    # "connect-src 'self' https://embed.tawk.to https://va.tawk.to; "
    # "frame-src https://embed.tawk.to; "
    # "worker-src 'self' blob:; "
    # "media-src 'self' data:; ")

    #     response.headers['Content-Security-Policy'] = csp_policy
    #     response.headers['X-Content-Type-Options'] = 'nosniff'
    #     response.headers['X-Frame-Options'] = 'DENY'
        return response


    # Import blueprints and models AFTER initializing extensions
    with app.app_context():
        from . import models
        from .auth import routes as auth_routes
        from .admin import routes as admin_routes
        from .views import views_bp
        from .messaging import routes as messaging_routes
        from .events import routes as events_routes
        from .jobs import routes as jobs_routes
        from .main import main_bp
        
        # Register blueprints
        app.register_blueprint(auth_routes.auth_bp)
        app.register_blueprint(admin_routes.admin_bp)
        app.register_blueprint(views_bp)
        app.register_blueprint(messaging_routes.messaging_bp)
        app.register_blueprint(events_routes.events_bp, url_prefix='/events')
        app.register_blueprint(jobs_routes.jobs_bp, url_prefix='/jobs')
        app.register_blueprint(main_bp, url_prefix='/')
    
    # Register CLI commands
    from .cli import register_commands
    register_commands(app)
    

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    return app