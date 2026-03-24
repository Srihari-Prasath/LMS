import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'alms-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings
    MAIL_ENABLED = os.environ.get('MAIL_ENABLED', 'false').lower() == 'true'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

    # Library settings
    FINE_PER_DAY = 5  # rupees
    LOAN_PERIOD_DAYS = 14

    # QR code directory
    QR_CODE_DIR = os.path.join(BASE_DIR, 'static', 'qrcodes')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'lms.db')


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'lms.db'))
