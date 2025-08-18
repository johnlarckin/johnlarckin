import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Babel configuration
    SUPPORTED_LANGUAGES = ['ru', 'en']
    DEFAULT_LANGUAGE = 'ru'
