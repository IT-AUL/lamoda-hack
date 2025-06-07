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
                {"role": "system", "text": """SYSTEM: Вы проверяете корректность карточки товара маркетплейса Lamoda. Вам передаётся JSON, в котором содержатся следующие поля:
 • name (string): обязательное, не должно быть пустым.
 • brand (string): обязательное, не пустое.
 • price (number): обязательное, положительное число больше нуля.
 • currency (string): обязательно, должно быть строго “RUB”.
 • gender (string): допустимые значения — “male”, “female”, “common”, “kids”.
 • sizes (array of strings): обязательное, должен быть непустой список, каждый элемент — строка (например, [“XS”, “S”, “M”]).
 • colors (array of strings): обязательное, должен быть непустой список, каждый элемент — строка.
 • images (array of strings): обязательное, список URL изображений, минимум одно.
 • description (string): необязательное, но если есть, должно быть строкой.
 • in_stock (boolean): по умолчанию true. Если указано — должно быть true или false.
 • tags (array of strings): необязательно, если указано — список строк.
 • season (string): обязательное, допустимые значения — “зима”, “весна”, “лето”, “осень”, “мульти”.
 • created_at (string, ISO 8601): обязательное, корректная дата в формате YYYY-MM-DDTHH:MM:SS.
 • seller_id (string): обязательное, строка, минимум 8 символов.

На основе этого:
 1. Проверь каждое поле на соответствие формату и требованиям.
 2. Если все поля корректны — верни JSON: { “status”: “ACCEPT”, “comments”: [] }
 3. Если есть ошибки — верни JSON: { “status”: “REJECT”, “comments”: [“Missing brand”, “price must be positive”, “invalid gender value”, “images must contain at least one valid URL”] }

Пиши только JSON-ответ, никаких объяснений или приветствий. Ответ должен быть строго валидным JSON-объектом. Учитывай, что даже при наличии одного нарушения — статус должен быть “REJECT”.

END SYSTEM
"""},
                {"role": "user", "text": text}
            ]
        }
    ).json()['result']['alternatives'][0]['message']['text']
    return response