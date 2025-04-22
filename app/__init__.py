
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import razorpay
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Razorpay client
razorpay_client = razorpay.Client(auth=("rzp_test_0CoFmwwua3jG0b", "elCMM9qPz8UDQ6FBnJRcO7DZ"))

def create_app():
    # Initialize Flask app
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1447@localhost/moviedb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
