# Holds SQLAlchemy database instance and other Flask extensions
from flask_wtf.csrf import CSRFProtect

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
