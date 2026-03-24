from datetime import datetime
from extensions import db


class IssuedBook(db.Model):
    __tablename__ = 'issued_books'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    fine = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='issued')  # issued / returned / overdue

    @property
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return datetime.utcnow() > self.due_date

    @property
    def days_remaining(self):
        if self.status == 'returned':
            return 0
        delta = (self.due_date - datetime.utcnow()).days
        return max(delta, 0)

    @property
    def overdue_days(self):
        if not self.is_overdue:
            return 0
        end = self.return_date if self.return_date else datetime.utcnow()
        return (end - self.due_date).days

    def __repr__(self):
        return f'<IssuedBook {self.id} - {self.status}>'
