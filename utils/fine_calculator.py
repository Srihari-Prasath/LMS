from datetime import datetime
from extensions import db


def calculate_fine(issued_book, fine_per_day=5):
    if issued_book.status == 'returned' and issued_book.return_date:
        end_date = issued_book.return_date
    else:
        end_date = datetime.utcnow()

    if end_date <= issued_book.due_date:
        return 0.0

    overdue_days = (end_date - issued_book.due_date).days
    return overdue_days * fine_per_day


def update_overdue_statuses(fine_per_day=5):
    from models.issued_book import IssuedBook
    overdue = IssuedBook.query.filter(
        IssuedBook.status == 'issued',
        IssuedBook.due_date < datetime.utcnow()
    ).all()
    for record in overdue:
        record.status = 'overdue'
        record.fine = calculate_fine(record, fine_per_day)
    if overdue:
        db.session.commit()
