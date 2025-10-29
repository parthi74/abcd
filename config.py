import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://root:jaisudhan%401512@localhost/amconnect_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False