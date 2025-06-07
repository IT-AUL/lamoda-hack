from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iin = db.Column(db.String(12), unique=True, nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    bank_account = db.Column(db.String(64), nullable=False)
    legal_address = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
