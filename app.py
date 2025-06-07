from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import check_password_hash

from config import Config
from models import db, Seller
from routes.products import product_bp
from utils import generate_random_password, generate_username, send_email_mock

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)
with app.app_context():
    db.create_all()
app.register_blueprint(product_bp)


@app.route("/registration", methods=["POST"])
def register_seller():
    data = request.get_json()

    if Seller.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Пользователь с такой почтой уже существует"}), 400

    if Seller.query.filter_by(inn=data["inn"]).first():
        return jsonify({"message": "Пользователь с таким ИИН уже существует"}), 400

    password = generate_random_password()
    login = generate_username(data["email"])

    seller = Seller(
        inn=data["inn"],
        company_name=data["company_name"],
        bank_account=data["bank_account"],
        legal_address=data["legal_address"],
        email=data["email"],
        login=login
    )
    seller.set_password(password)

    db.session.add(seller)
    db.session.commit()

    # Отправляем "письмо"
    send_email_mock(
        to=data["email"],
        subject="Добро пожаловать",
        body=f"Ваш логин: {login}\nВаш пароль: {password}"
    )

    access_token = create_access_token(identity=str(seller.id))
    refresh_token = create_refresh_token(identity=str(seller.id))

    return jsonify({
        "message": "Регистрация прошла успешно",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "login": login,
        "password": password
    }), 201


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"msg": "Email и пароль обязательны"}), 400

    seller = Seller.query.filter_by(login=login).first()
    if not seller or not check_password_hash(seller.password_hash, password):
        return jsonify({"msg": "Неверный логин или пароль"}), 401

    access_token = create_access_token(identity=seller.id)
    refresh_token = create_refresh_token(identity=seller.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
