import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost:3306/betterlupin'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

