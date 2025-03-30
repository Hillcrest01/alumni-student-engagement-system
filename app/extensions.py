from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions without app context
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()