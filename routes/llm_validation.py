import requests as r
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

llm_validation_bp = Blueprint('llm_validation', __name__, url_prefix='/validation')


@llm_validation_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.json
    current_user_id = get_jwt_identity()

    text = request.json.get('text')
    response = llm_validation(text)
    return jsonify({"response": response})


def llm_validation(text):
    api_key = "AQVNwwTX86U4EIzYGcrEgsbhNqVPleGGWfHfK3hl"

    response = r.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers={"Authorization": f"Api-Key {api_key}"},
        json={
            "modelUri": f"gpt://{"b1gbj6sdr59ilf9lvia5"}/yandexgpt-lite",
            "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "2000"},
            "messages": [
                {"role": "system", "text": "Найди ошибки в тексте и исправь их"},
                {"role": "user", "text": text}
            ]
        }
    ).json()['result']['alternatives'][0]['message']['text']
    return response
