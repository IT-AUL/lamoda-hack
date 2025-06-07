import datetime
import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Seller(db.Model):
    __tablename__ = "seller"

    id = db.Column(db.Integer, primary_key=True)
    iin = db.Column(db.String(12), unique=True, nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    bank_account = db.Column(db.String(64), nullable=False)
    legal_address = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    products = db.relationship('ProductCard', back_populates='seller', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ProductCard(db.Model):
    __tablename__ = 'product_card'

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    price = db.Column(db.Float)
    currency = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    sizes = db.Column(JSON)  # Заменяем ARRAY на JSON
    colors = db.Column(JSON)  # Заменяем ARRAY на JSON
    images = db.Column(JSON)  # Заменяем ARRAY на JSON
    description = db.Column(db.Text)
    in_stock = db.Column(db.Boolean, default=True)
    tags = db.Column(JSON)  # Заменяем ARRAY на JSON
    season = db.Column(JSON)  # Заменяем ARRAY на JSON
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    type = db.Column(db.String(50))
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    seller = db.relationship('Seller', back_populates='products')

    __mapper_args__ = {
        'polymorphic_identity': 'product',
        'polymorphic_on': type
    }


class TShirt(ProductCard):
    __tablename__ = 'tshirt'

    id = db.Column(db.String, db.ForeignKey('product_card.id'), primary_key=True)
    material = db.Column(db.String(100))  # хлопок, полиэстер и т.п.
    sleeve_length = db.Column(db.String(50))  # короткий, длинный

    __mapper_args__ = {
        'polymorphic_identity': 'tshirt',
    }


class Pants(ProductCard):
    __tablename__ = 'pants'

    id = db.Column(db.String, db.ForeignKey('product_card.id'), primary_key=True)
    waist_type = db.Column(db.String(50))  # высокая, средняя, низкая
    length = db.Column(db.String(50))  # полная длина, шорты и т.п.

    __mapper_args__ = {
        'polymorphic_identity': 'pants',
    }