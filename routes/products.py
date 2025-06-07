from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ProductCard, TShirt, Pants, Seller
from datetime import datetime

product_bp = Blueprint('product', __name__, url_prefix='/products')


@product_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.json
    current_user_id = get_jwt_identity()

    category = data.get('category')
    common_fields = {
        "name": data.get("name"),
        "brand": data.get("brand"),
        "price": data.get("price"),
        "currency": data.get("currency"),
        "gender": data.get("gender"),
        "sizes": data.get("sizes"),
        "colors": data.get("colors"),
        "images": data.get("images"),
        "description": data.get("description"),
        "in_stock": data.get("in_stock", True),
        "tags": data.get("tags"),
        "season": data.get("season"),
        "created_at": datetime.utcnow(),
        "seller_id": current_user_id
    }

    if category == "tshirt":
        product = TShirt(**common_fields,
                         category="tshirt",
                         material=data.get("material"),
                         sleeve_length=data.get("sleeve_length"))
    elif category == "pants":
        product = Pants(**common_fields,
                        category="pants",
                        waist_type=data.get("waist_type"),
                        length=data.get("length"))
    else:
        product = ProductCard(**common_fields, category=category)

    db.session.add(product)
    db.session.commit()
    return jsonify({"id": product.id}), 201


@product_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    current_user_id = get_jwt_identity()
    products = ProductCard.query.filter_by(seller_id=current_user_id).all()
    return jsonify([serialize_product(p) for p in products])


@product_bp.route('/<string:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    current_user_id = get_jwt_identity()
    seller = Seller.query.get(current_user_id)
    if not seller:
        return jsonify({"message": "User not found"}), 404
    if seller.products.filter_by(id=product_id).first() is None:
        return jsonify({"message": "Product not found"}), 404

    product = ProductCard.query.get_or_404(product_id)
    return jsonify(serialize_product(product))


@product_bp.route('/<string:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    current_user_id = get_jwt_identity()
    seller = Seller.query.get(current_user_id)
    if not seller:
        return jsonify({"message": "User not found"}), 404
    if seller.products.filter_by(id=product_id).first() is None:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    product = ProductCard.query.get_or_404(product_id)

    for field in ["name", "brand", "price", "currency", "gender",
                  "sizes", "colors", "images", "description",
                  "in_stock", "tags", "season"]:
        if field in data:
            setattr(product, field, data[field])

    if isinstance(product, TShirt):
        product.material = data.get("material", product.material)
        product.sleeve_length = data.get("sleeve_length", product.sleeve_length)
    elif isinstance(product, Pants):
        product.waist_type = data.get("waist_type", product.waist_type)
        product.length = data.get("length", product.length)

    db.session.commit()
    return jsonify(serialize_product(product))


@product_bp.route('/<string:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user_id = get_jwt_identity()
    seller = Seller.query.get(current_user_id)
    if not seller:
        return jsonify({"message": "User not found"}), 404
    if seller.products.filter_by(id=product_id).first() is None:
        return jsonify({"message": "Product not found"}), 404
    product = ProductCard.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200


def serialize_product(p):
    base = {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "brand": p.brand,
        "price": p.price,
        "currency": p.currency,
        "gender": p.gender,
        "sizes": p.sizes,
        "colors": p.colors,
        "images": p.images,
        "description": p.description,
        "in_stock": p.in_stock,
        "tags": p.tags,
        "season": p.season,
        "created_at": p.created_at.isoformat()
    }

    if isinstance(p, TShirt):
        base["material"] = p.material
        base["sleeve_length"] = p.sleeve_length
    elif isinstance(p, Pants):
        base["waist_type"] = p.waist_type
        base["length"] = p.length

    return base
