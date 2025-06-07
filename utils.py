import random
import string


def generate_random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_username(email):
    base = email.split('@')[0]
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{base}_{suffix}"


def send_email_mock(to, subject, body):
    # 🧪 Мок функции отправки письма
    print(f"\n=== Email to: {to} ===\nSubject: {subject}\n{body}\n=======================\n")
