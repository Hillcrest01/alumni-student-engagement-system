from flask import Flask, render_template
from config import Config
from .extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Local import to avoid circular dependency
        return User.query.get(int(user_id))
    
    # Security headers
    @app.after_request
    def apply_security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    # Import blueprints and models AFTER initializing extensions
    with app.app_context():
        from . import models
        from .auth import routes as auth_routes
        from .admin import routes as admin_routes
        
        # Register blueprints
        app.register_blueprint(auth_routes.auth_bp)
        app.register_blueprint(admin_routes.admin_bp)
    
    # Register CLI commands
    from .cli import register_commands
    register_commands(app)
    

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    return app