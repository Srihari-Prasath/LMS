from extensions import db


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, default=0.0)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', name='uq_user_category'),
    )

    def __repr__(self):
        return f'<Recommendation user={self.user_id} cat={self.category} score={self.score}>'
