import click
from app import db
from app.models import User

def register_commands(app):
    @app.cli.command("create-admin")
    @click.option('--email', prompt=True)
    @click.option('--password', prompt=True, hide_input=True)
    def create_admin(email, password):
        """Create admin user with full privileges"""
        if User.query.filter_by(email=email).first():
            click.echo(f"Error: Email {email} already exists!")
            return

        admin = User(
            email=email,
            role='admin',
            is_verified=True,
            profile_complete=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Admin {email} created successfully!")

    @app.cli.command("seed-interests")
    def seed_interests():
        """Add default interests to database"""
        from app.models import Interest
        Interest.seed_default_interests()
        print("Default interests added to database!")