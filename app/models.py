from app import db
from datetime import datetime

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), index=True, nullable=False)
    preferred_name = db.Column(db.String(64), index=True)
    zip_code = db.Column(db.String(10), index=True, nullable=False)
    birth_date = db.Column(db.Date, index=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Customer {self.full_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'preferred_name': self.preferred_name,
            'zip_code': self.zip_code,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'email': self.email,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None
        }
