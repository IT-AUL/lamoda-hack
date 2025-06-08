import requests as r
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

import utils
from config import Config

llm_validation_bp = Blueprint('llm_validation', __name__, url_prefix='/validation')
prompt = utils.get_prompt()


@llm_validation_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.json
    current_user_id = get_jwt_identity()

    text = request.json.get('text')
    response = llm_validation(text)
    return jsonify({"response": response})


def llm_validation(text):
    api_key = Config.API_KEY
    folder_id = Config.FOLDER_ID
    model_id = Config.MODEL

    response = r.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers={"Authorization": f"Api-Key {api_key}"},
        json={
            "modelUri": f"gpt://{folder_id}/{model_id}",
            "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "2000"},
            "messages": [
                {"role": "system", "text": prompt},
                {"role": "user", "text": text}
            ]
        }
    ).json()['result']['alternatives'][0]['message']['text']
    return response
