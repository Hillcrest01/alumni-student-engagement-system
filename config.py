import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    

    STATIC_FOLDER = 'static'
    # URL-encode special characters in password
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 
        'mysql://root:Kulundeng%2EJamach%2E1@localhost/alumni_db?charset=utf8mb4')
    
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 3600}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration (for future use)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'peterochieng008@gmail.com'
    MAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Peter Ochieng', 'peterochieng008@gmail.com')
    MAIL_SUPPRESS_SEND = False  # Set to True to suppress email sending in test mode

    RESET_TOKEN_EXPIRATION = 3600 

    # UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads' , 'events')
    # os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists