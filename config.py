import os
from sqlalchemy import create_engine

class Config():
    SECRET_KEY='CLAVE SECRETA'
    SESSION_COOKIE_SECURE=False

class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://Diana:1234@localhost/SweetDreams'