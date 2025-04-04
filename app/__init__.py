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

        csp_policy = (
        "default-src 'self';"
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
        "script-src 'self' https://cdn.jsdelivr.net;"
        "font-src 'self' data: https://cdn.jsdelivr.net;;"
        "img-src 'self' data:;"
        "connect-src 'self';"
    )
        response.headers['Content-Security-Policy'] = csp_policy
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
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