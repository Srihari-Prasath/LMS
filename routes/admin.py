from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from extensions import db
from models.user import User
from models.book import Book
from models.issued_book import IssuedBook
from utils.decorators import admin_required
from utils.fine_calculator import calculate_fine, update_overdue_statuses
from utils.qr_service import generate_qr
from utils.email_service import send_issue_notification, send_return_notification

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    update_overdue_statuses(current_app.config['FINE_PER_DAY'])

    stats = {
        'total_books': Book.query.count(),
        'total_students': User.query.filter_by(role='student').count(),
        'currently_issued': IssuedBook.query.filter(IssuedBook.status.in_(['issued', 'overdue'])).count(),
        'overdue_count': IssuedBook.query.filter_by(status='overdue').count(),
        'total_fines': db.session.query(db.func.sum(IssuedBook.fine)).scalar() or 0,
    }

    recent_issues = IssuedBook.query.order_by(IssuedBook.issue_date.desc()).limit(10).all()

    return render_template('admin/dashboard.html', stats=stats, recent_issues=recent_issues)


@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        isbn = request.form.get('isbn', '').strip()
        quantity = int(request.form.get('quantity', 1))
        description = request.form.get('description', '').strip()

        if not title or not author or not category or not isbn:
            flash('Title, Author, Category, and ISBN are required.', 'danger')
        elif Book.query.filter_by(isbn=isbn).first():
            flash('A book with this ISBN already exists.', 'danger')
        else:
            book = Book(
                title=title, author=author, category=category,
                isbn=isbn, quantity=quantity, description=description
            )
            db.session.add(book)
            db.session.commit()

            # Generate QR code
            qr_path = generate_qr(book)
            book.qr_code_path = qr_path
            db.session.commit()

            flash(f'Book "{title}" added successfully!', 'success')
            return redirect(url_for('books.list_books'))

    categories = db.session.query(Book.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('admin/add_book.html', categories=categories)


@admin_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.category = request.form.get('category', '').strip()
        book.isbn = request.form.get('isbn', '').strip()
        book.quantity = int(request.form.get('quantity', 1))
        book.description = request.form.get('description', '').strip()

        existing = Book.query.filter(Book.isbn == book.isbn, Book.id != book.id).first()
        if existing:
            flash('Another book with this ISBN already exists.', 'danger')
        else:
            db.session.commit()
            flash(f'Book "{book.title}" updated successfully!', 'success')
            return redirect(url_for('books.book_detail', book_id=book.id))

    categories = db.session.query(Book.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('admin/edit_book.html', book=book, categories=categories)


@admin_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    active_issues = IssuedBook.query.filter(
        IssuedBook.book_id == book_id,
        IssuedBook.status.in_(['issued', 'overdue'])
    ).count()

    if active_issues > 0:
        flash('Cannot delete a book that is currently issued.', 'danger')
        return redirect(url_for('books.book_detail', book_id=book_id))

    db.session.delete(book)
    db.session.commit()
    flash(f'Book "{book.title}" deleted.', 'success')
    return redirect(url_for('books.list_books'))


@admin_bp.route('/issue', methods=['GET', 'POST'])
@admin_required
def issue_book():
    if request.method == 'POST':
        book_id = request.form.get('book_id', type=int)
        user_id = request.form.get('user_id', type=int)
        loan_days = request.form.get('loan_days', type=int, default=current_app.config['LOAN_PERIOD_DAYS'])

        book = Book.query.get(book_id)
        user = User.query.get(user_id)

        if not book or not user:
            flash('Invalid book or student.', 'danger')
        elif not book.is_available:
            flash(f'"{book.title}" is not available.', 'danger')
        elif user.role != 'student':
            flash('Books can only be issued to students.', 'danger')
        else:
            due_date = datetime.utcnow() + timedelta(days=loan_days)
            issued = IssuedBook(
                book_id=book.id, user_id=user.id,
                due_date=due_date, status='issued'
            )
            db.session.add(issued)
            db.session.commit()

            send_issue_notification(user, book, due_date)
            flash(f'"{book.title}" issued to {user.name}. Due: {due_date.strftime("%d %b %Y")}', 'success')
            return redirect(url_for('admin.dashboard'))

    students = User.query.filter_by(role='student').order_by(User.name).all()
    books = Book.query.order_by(Book.title).all()
    available_books = [b for b in books if b.is_available]
    book_id = request.args.get('book_id', type=int)
    return render_template('admin/issue_book.html', students=students,
                           books=available_books, selected_book_id=book_id,
                           loan_days=current_app.config['LOAN_PERIOD_DAYS'])


@admin_bp.route('/return/<int:issued_id>', methods=['POST'])
@admin_required
def return_book(issued_id):
    issued = IssuedBook.query.get_or_404(issued_id)
    if issued.status == 'returned':
        flash('This book has already been returned.', 'warning')
        return redirect(url_for('admin.dashboard'))

    issued.return_date = datetime.utcnow()
    issued.fine = calculate_fine(issued, current_app.config['FINE_PER_DAY'])
    issued.status = 'returned'
    db.session.commit()

    send_return_notification(issued.user, issued.book, issued.fine)

    if issued.fine > 0:
        flash(f'Book returned. Fine: Rs. {issued.fine}', 'warning')
    else:
        flash('Book returned successfully!', 'success')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/issued')
@admin_required
def issued_books():
    update_overdue_statuses(current_app.config['FINE_PER_DAY'])
    status_filter = request.args.get('status', 'all')

    query = IssuedBook.query
    if status_filter == 'issued':
        query = query.filter_by(status='issued')
    elif status_filter == 'overdue':
        query = query.filter_by(status='overdue')
    elif status_filter == 'returned':
        query = query.filter_by(status='returned')

    records = query.order_by(IssuedBook.issue_date.desc()).all()
    return render_template('admin/issued_books.html', records=records, status_filter=status_filter)


@admin_bp.route('/analytics')
@admin_required
def analytics():
    stats = {
        'total_books': Book.query.count(),
        'total_copies': db.session.query(db.func.sum(Book.quantity)).scalar() or 0,
        'total_students': User.query.filter_by(role='student').count(),
        'currently_issued': IssuedBook.query.filter(IssuedBook.status.in_(['issued', 'overdue'])).count(),
        'overdue_count': IssuedBook.query.filter_by(status='overdue').count(),
        'total_fines': db.session.query(db.func.sum(IssuedBook.fine)).scalar() or 0,
        'total_returned': IssuedBook.query.filter_by(status='returned').count(),
    }

    # Most issued books (top 10)
    most_issued = [tuple(row) for row in db.session.query(
        Book.title, db.func.count(IssuedBook.id).label('count')
    ).join(IssuedBook).group_by(Book.id)
        .order_by(db.desc('count')).limit(10).all()]

    # Category distribution
    cat_dist = [tuple(row) for row in db.session.query(
        Book.category, db.func.count(Book.id)
    ).group_by(Book.category).all()]

    # Monthly issue trends (last 12 months)
    monthly = [tuple(row) for row in db.session.query(
        db.func.strftime('%Y-%m', IssuedBook.issue_date).label('month'),
        db.func.count(IssuedBook.id)
    ).group_by('month').order_by('month').all()]

    # Most active students
    active_users = [tuple(row) for row in db.session.query(
        User.name, db.func.count(IssuedBook.id).label('count')
    ).join(IssuedBook).filter(User.role == 'student')
        .group_by(User.id).order_by(db.desc('count')).limit(10).all()]

    return render_template('admin/analytics.html',
                           stats=stats,
                           most_issued=most_issued,
                           cat_dist=cat_dist,
                           monthly=monthly,
                           active_users=active_users)


# ── Student Management ──────────────────────────────────────────

@admin_bp.route('/students')
@admin_required
def students():
    search = request.args.get('q', '').strip()
    query = User.query.filter_by(role='student')

    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )

    all_students = query.order_by(User.name).all()

    # Compute stats per student
    student_stats = []
    for s in all_students:
        issued_count = IssuedBook.query.filter(
            IssuedBook.user_id == s.id,
            IssuedBook.status.in_(['issued', 'overdue'])
        ).count()
        overdue_count = IssuedBook.query.filter_by(user_id=s.id, status='overdue').count()
        total_read = IssuedBook.query.filter_by(user_id=s.id, status='returned').count()
        total_fine = db.session.query(db.func.sum(IssuedBook.fine)).filter(
            IssuedBook.user_id == s.id,
            IssuedBook.fine > 0
        ).scalar() or 0

        student_stats.append({
            'student': s,
            'issued': issued_count,
            'overdue': overdue_count,
            'returned': total_read,
            'fine': total_fine,
        })

    return render_template('admin/students.html', student_stats=student_stats, search=search)


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
        else:
            student = User(name=name, email=email, role='student')
            student.set_password(password)
            db.session.add(student)
            db.session.commit()
            flash(f'Student "{name}" added successfully!', 'success')
            return redirect(url_for('admin.students'))

    return render_template('admin/add_student.html')


@admin_bp.route('/students/<int:student_id>')
@admin_required
def student_detail(student_id):
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        flash('Not a student account.', 'danger')
        return redirect(url_for('admin.students'))

    update_overdue_statuses(current_app.config['FINE_PER_DAY'])

    current_books = IssuedBook.query.filter(
        IssuedBook.user_id == student_id,
        IssuedBook.status.in_(['issued', 'overdue'])
    ).order_by(IssuedBook.due_date).all()

    returned_books = IssuedBook.query.filter_by(
        user_id=student_id, status='returned'
    ).order_by(IssuedBook.return_date.desc()).all()

    total_fine = db.session.query(db.func.sum(IssuedBook.fine)).filter(
        IssuedBook.user_id == student_id,
        IssuedBook.fine > 0
    ).scalar() or 0

    return render_template('admin/student_detail.html',
                           student=student,
                           current_books=current_books,
                           returned_books=returned_books,
                           total_fine=total_fine)


@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        flash('Not a student account.', 'danger')
        return redirect(url_for('admin.students'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email:
            flash('Name and email are required.', 'danger')
        else:
            existing = User.query.filter(User.email == email, User.id != student.id).first()
            if existing:
                flash('Another user with this email already exists.', 'danger')
            else:
                student.name = name
                student.email = email
                if password:
                    student.set_password(password)
                db.session.commit()
                flash(f'Student "{name}" updated successfully!', 'success')
                return redirect(url_for('admin.student_detail', student_id=student.id))

    return render_template('admin/edit_student.html', student=student)


@admin_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        flash('Not a student account.', 'danger')
        return redirect(url_for('admin.students'))

    active_issues = IssuedBook.query.filter(
        IssuedBook.user_id == student_id,
        IssuedBook.status.in_(['issued', 'overdue'])
    ).count()

    if active_issues > 0:
        flash('Cannot delete a student who has books currently issued. Return all books first.', 'danger')
        return redirect(url_for('admin.student_detail', student_id=student_id))

    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{student.name}" deleted.', 'success')
    return redirect(url_for('admin.students'))
