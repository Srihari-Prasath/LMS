from flask import Blueprint, render_template, current_app
from flask_login import current_user
from extensions import db
from models.issued_book import IssuedBook
from utils.decorators import student_required
from utils.fine_calculator import update_overdue_statuses
from utils.recommendation_engine import get_recommendations

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@student_required
def dashboard():
    update_overdue_statuses(current_app.config['FINE_PER_DAY'])

    current_books = IssuedBook.query.filter(
        IssuedBook.user_id == current_user.id,
        IssuedBook.status.in_(['issued', 'overdue'])
    ).order_by(IssuedBook.due_date).all()

    total_fine = sum(ib.fine for ib in current_books if ib.fine > 0)
    total_read = IssuedBook.query.filter_by(user_id=current_user.id, status='returned').count()

    recommendations = get_recommendations(current_user.id, limit=4)

    return render_template('student/dashboard.html',
                           current_books=current_books,
                           total_fine=total_fine,
                           total_read=total_read,
                           recommendations=recommendations)


@student_bp.route('/my-books')
@student_required
def my_books():
    update_overdue_statuses(current_app.config['FINE_PER_DAY'])

    issued = IssuedBook.query.filter(
        IssuedBook.user_id == current_user.id,
        IssuedBook.status.in_(['issued', 'overdue'])
    ).order_by(IssuedBook.due_date).all()

    returned = IssuedBook.query.filter_by(
        user_id=current_user.id, status='returned'
    ).order_by(IssuedBook.return_date.desc()).all()

    total_fine = sum(ib.fine for ib in issued if ib.fine > 0)

    return render_template('student/my_books.html',
                           issued=issued, returned=returned, total_fine=total_fine)


@student_bp.route('/recommendations')
@student_required
def recommendations():
    recs = get_recommendations(current_user.id, limit=12)
    return render_template('student/recommendations.html', recommendations=recs)
