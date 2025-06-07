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
                {"role": "system", "text": """SYSTEM:
Вы — помощник проверки карточек товара Lamoda. У вас есть чёткий чек-лист обязательных атрибутов (brand, title, category, size_scale, collection, main_category, type, gender, season, color, composition, tn_ved, eac, barcode, tax_class, price, sale_price with dates, parent_sku, size_value, seller_sku, production_country, producer_name, producer_address, expiration_period, warranty_period). Принимаете JSON с заполнением атрибутов и выдаёте строго JSON-ответ:

- “status”: “ACCEPT” — если все поля заполнены корректно.  
- “status”: “REJECT” — если найдены ошибки.

Если REJECT — добавляете поле “comments” с массивом коротких сообщений с конкретными нарушениями чек-листа, например:
“Missing brand”, “Barcode has wrong length”, “Price mismatch between sizes”.

Проверяйте именно следующие требования:

1. **brand** — обязательный, из справочника.
2. **title** — обязательный, не пустой.
3. **category** — одна или несколько, проверка по справочнику категорий.
4. **size_scale** и **size_system** — обязательны, из справочника; NS для косметики и некоторых категорий.
5. **collection** — корректный сезон и год (осень‑зима нач. 01.07, весна‑лето нач. 01.01).
6. **main_category** — из справочника “Основная категория”.
7. **type** — точное соответствие справочнику соответствий категории‑типа.
8. **gender**, **season**, **color** — обязательны и корректны: gender: male/female/common/kids; season из справочника; color — один, мультиколор или «прозрачный» для косметики.
9. **composition** — указано в % строго суммой 100%, по ярлыку, без аббревиатур.
10. **tn_ved** — обязательный, из справочника.
11. **eac** — “1” или должна быть ссылка на отказное письмо.
12. **barcode** — EAN‑13 (13 цифр) или EAN‑8 (8 цифр), уникальный.
13. **tax_class** — для ОСН: 5%, 7%, 10%, 20%; для УСН: “Без НДС”.
14. **price** — указан, одинаков для всех размеров.
15. **sale_price** (если указан) — скидка 5–80% от price.
16. **sale_start_date**, **sale_end_date** (если sale_price есть) — формат “YYYY‑MM‑DD HH:MM”, не раньше времени загрузки.
17. **parent_sku** — 5–50 символов, объединяет все размеры одного артикула, без дубликатов размеров.
18. **size_value** — соответствует ярлыку; для одноразмерных — “00”.
19. **seller_sku** — уникальный на размер, 5–50 символов.
20. **production_country** — из справочника (русский язык).
21. **producer_name**, **producer_address** — совпадают с документацией и этикеткой.
22. **expiration_period**, **warranty_period** — указаны: число + единица (дни/мес/лет) или “не установлен”.

Вы отвечаете строго JSON-объектом с двумя полями:

```json
{
  "status": "ACCEPT",
  "comments": []
}
или:
{
  "status": "REJECT",
  "comments": ["Missing brand", "Composition sums to 95%", "Barcode has wrong length"]
}
Никакого другого текста, ни приветствий, ни объяснений. Только валидный JSON.
END SYSTEM
"""},
                {"role": "user", "text": text}
            ]
        }
    ).json()['result']['alternatives'][0]['message']['text']
    return response

print(llm_validation("""{
  "name": "Кроссовки",
  "brand": null,
  "price": 5000,
  "currency": "RUB",
  "gender": "unisex",
  "sizes": ["39", "40", "41"],
  "colors": ["черный"],
  "images": ["image1.jpg", "image2.jpg"],
  "description": "Стильные кроссовки для повседневной носки",
  "in_stock": true,
  "tags": ["спорт", "уличный стиль"],
  "season": "лето",
  "created_at": "2023-10-25T12:00:00",
  "seller_id": "user123"
}"""))