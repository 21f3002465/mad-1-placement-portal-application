import os

class Config:
    SECRET_KEY = 'placement_data'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement-database.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATION = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_UPLOAD_LENGTH = 16*1034*1024