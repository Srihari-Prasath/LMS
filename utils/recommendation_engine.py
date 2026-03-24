from collections import Counter
from extensions import db
from models.issued_book import IssuedBook
from models.book import Book
from models.recommendation import Recommendation


def compute_recommendations(user_id):
    issued = IssuedBook.query.filter_by(user_id=user_id).all()
    book_ids = [ib.book_id for ib in issued]

    if not book_ids:
        return

    books = Book.query.filter(Book.id.in_(book_ids)).all()
    category_counts = Counter(b.category for b in books)
    total = sum(category_counts.values()) or 1

    Recommendation.query.filter_by(user_id=user_id).delete()

    for category, count in category_counts.items():
        rec = Recommendation(
            user_id=user_id,
            category=category,
            score=round(count / total, 2)
        )
        db.session.add(rec)
    db.session.commit()


def get_recommendations(user_id, limit=10):
    compute_recommendations(user_id)

    recs = Recommendation.query.filter_by(user_id=user_id) \
        .order_by(Recommendation.score.desc()).limit(5).all()
    top_categories = [r.category for r in recs]

    if not top_categories:
        return Book.query.order_by(Book.added_date.desc()).limit(limit).all()

    issued_book_ids = [ib.book_id for ib in
                       IssuedBook.query.filter_by(user_id=user_id).all()]

    query = Book.query.filter(Book.category.in_(top_categories))
    if issued_book_ids:
        query = query.filter(~Book.id.in_(issued_book_ids))

    recommended = query.limit(limit).all()

    if len(recommended) < limit:
        remaining = limit - len(recommended)
        exclude_ids = issued_book_ids + [b.id for b in recommended]
        extra = Book.query.filter(~Book.id.in_(exclude_ids)).limit(remaining).all() if exclude_ids else []
        recommended.extend(extra)

    return recommended
