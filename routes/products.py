import json
import os
import tempfile
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, ProductCard, TShirt, Pants, Seller
from datetime import datetime
from utils import upload2bucket
import pandas as pd

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
        "created_at": datetime.now(),
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


@product_bp.route('/paginated', methods=['GET'])
@jwt_required()
def get_products_paginated():
    current_user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    pagination = ProductCard.query.filter_by(seller_id=current_user_id).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    return jsonify({
        "products": [serialize_product(p) for p in pagination.items],
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages
    })


@product_bp.route('/upload-excel', methods=['POST'])
@jwt_required()
def upload_excel():
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({"message": "Файл не найден"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Файл не выбран"}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"message": "Поддерживаются только Excel файлы"}), 400
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            file.save(tmp_file.name)
            df = pd.read_excel(tmp_file.name)
            os.unlink(tmp_file.name)
        
        created_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                product_data = validate_excel_row(row)
                if product_data is None:
                    errors.append(f"Строка {index + 2}: Отсутствуют обязательные поля")
                    continue
                
                category = product_data.get('category', '').lower()
                common_fields = {
                    **product_data,
                    "seller_id": current_user_id,
                    "created_at": datetime.now()
                }
                
                if category == "tshirt":
                    product = TShirt(**common_fields,
                                   material=row.get("material"),
                                   sleeve_length=row.get("sleeve_length"))
                elif category == "pants":
                    product = Pants(**common_fields,
                                  waist_type=row.get("waist_type"),
                                  length=row.get("length"))
                else:
                    product = ProductCard(**common_fields)
                
                db.session.add(product)
                created_count += 1
                
            except Exception as e:
                errors.append(f"Строка {index + 2}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            "message": f"Обработка завершена",
            "created": created_count,
            "errors": errors
        })
        
    except Exception as e:
        return jsonify({"message": f"Ошибка обработки файла: {str(e)}"}), 500


@product_bp.route('/all', methods=['DELETE'])
@jwt_required()
def delete_all_products():
    current_user_id = get_jwt_identity()
    products = ProductCard.query.filter_by(seller_id=current_user_id).all()
    deleted_count = len(products)
    
    for product in products:
        db.session.delete(product)
    
    db.session.commit()
    
    return jsonify({
        "message": "Все карточки удалены",
        "deleted_count": deleted_count
    })


@product_bp.route('/<string:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    current_user_id = get_jwt_identity()
    seller = Seller.query.get(current_user_id)
    if not seller:
        return jsonify({"message": "User not found"}), 404
    product = next((p for p in seller.products if str(p.id) == product_id), None)
    if not product:
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
    product = next((p for p in seller.products if str(p.id) == product_id), None)
    if not product:
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
    product = next((p for p in seller.products if str(p.id) == product_id), None)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    product = ProductCard.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200


def validate_excel_row(row):
    required_fields = ['name']
    for field in required_fields:
        if pd.isna(row.get(field)) or str(row.get(field)).strip() == '':
            return None
    
    def safe_json_parse(value):
        if pd.isna(value) or value == '':
            return []
        try:
            if isinstance(value, str):
                return json.loads(value)
            return value if isinstance(value, list) else [value]
        except:
            return [str(value)]
    
    return {
        "name": str(row.get("name", "")).strip(),
        "category": str(row.get("category", "")).strip(),
        "brand": str(row.get("brand", "")).strip() if not pd.isna(row.get("brand")) else None,
        "price": float(row.get("price")) if not pd.isna(row.get("price")) else None,
        "currency": str(row.get("currency", "")).strip() if not pd.isna(row.get("currency")) else None,
        "gender": str(row.get("gender", "")).strip() if not pd.isna(row.get("gender")) else None,
        "sizes": safe_json_parse(row.get("sizes")),
        "colors": safe_json_parse(row.get("colors")),
        "description": str(row.get("description", "")).strip() if not pd.isna(row.get("description")) else None,
        "tags": safe_json_parse(row.get("tags")),
        "season": safe_json_parse(row.get("season")),
        "in_stock": True
    }


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
