from models.user import User
from models.book import Book
from models.issued_book import IssuedBook
from models.recommendation import Recommendation
from extensions import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


__all__ = ['User', 'Book', 'IssuedBook', 'Recommendation']
