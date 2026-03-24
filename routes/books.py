from flask import Blueprint, render_template, request
from flask_login import login_required
from extensions import db
from models.book import Book

books_bp = Blueprint('books', __name__)


@books_bp.route('/')
@login_required
def list_books():
    search = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    availability = request.args.get('availability', '')

    query = Book.query

    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        )

    if category:
        query = query.filter_by(category=category)

    books = query.order_by(Book.title).all()

    if availability == 'available':
        books = [b for b in books if b.is_available]
    elif availability == 'out':
        books = [b for b in books if not b.is_available]

    categories = db.session.query(Book.category).distinct().order_by(Book.category).all()
    categories = [c[0] for c in categories]

    return render_template('books/list.html', books=books, categories=categories,
                           search=search, selected_category=category,
                           selected_availability=availability)


@books_bp.route('/<int:book_id>')
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    from models.issued_book import IssuedBook
    history = IssuedBook.query.filter_by(book_id=book_id) \
        .order_by(IssuedBook.issue_date.desc()).limit(20).all()
    return render_template('books/detail.html', book=book, history=history)
