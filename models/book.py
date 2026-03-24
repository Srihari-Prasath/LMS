from datetime import datetime
from extensions import db


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    qr_code_path = db.Column(db.String(200))
    description = db.Column(db.Text, default='')
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

    issued_records = db.relationship('IssuedBook', backref='book', lazy=True)

    @property
    def available_quantity(self):
        from models.issued_book import IssuedBook
        issued_count = IssuedBook.query.filter(
            IssuedBook.book_id == self.id,
            IssuedBook.status.in_(['issued', 'overdue'])
        ).count()
        return self.quantity - issued_count

    @property
    def is_available(self):
        return self.available_quantity > 0

    def __repr__(self):
        return f'<Book {self.title}>'
