# Server configuration
HOST = '127.0.0.1'
PORT = 5001

# Pagination
RECORDS_PER_PAGE = 10

# Database
DATABASE_URL = 'sqlite:///manifest.db'

class Config:
    """Flask application configuration class"""
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dev'
    DEBUG = True
