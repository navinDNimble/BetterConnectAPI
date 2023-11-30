from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')  # Assuming your configuration is in the 'config' module
db = SQLAlchemy(app)

from app import routes  # Import routes after 'db' is defined to avoid circular imports
