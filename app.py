import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from config import DevelopmentConfig
from extensions import db, login_manager, csrf


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.student import student_bp
    from routes.books import books_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(books_bp, url_prefix='/books')

    # Create tables and directories
    with app.app_context():
        from models import User, Book, IssuedBook, Recommendation
        db.create_all()
        os.makedirs(app.config['QR_CODE_DIR'], exist_ok=True)

    # Register template helpers
    from utils.helpers import format_date, format_datetime, time_ago
    app.jinja_env.globals.update(
        format_date=format_date,
        format_datetime=format_datetime,
        time_ago=time_ago,
    )

    # Root route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('auth.login'))

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return '<h1>403 - Access Denied</h1><p>You do not have permission to access this page.</p>', 403

    @app.errorhandler(404)
    def not_found(e):
        return '<h1>404 - Page Not Found</h1><p>The page you are looking for does not exist.</p>', 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
