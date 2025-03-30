import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    # Cryptographic key for session security
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    
    # MySQL connection string format:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
        'mysql://root:Peter.Omondi.1@localhost/alumni_db?charset=utf8mb4')
    
    # Prevent connection timeout (MySQL defaults to 8hr wait_timeout)
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 3600}
    
    # Disable Flask-SQLAlchemy event system (saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False