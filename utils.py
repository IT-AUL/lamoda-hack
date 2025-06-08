import os
import uuid

from s3 import s3service, generate_presigned_url

s3 = s3service()


def generate_random_password(length=10):
    return "12345"
    # return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_username(email):
    base = email.split('@')[0]
    # suffix = ''.join(random.choices(string.digits, k=4))
    # return f"{base}_{suffix}"
    prefix = "login"
    return f"{prefix}_{base}"


def send_email_mock(to, subject, body):
    print(f"\n=== Email to: {to} ===\nSubject: {subject}\n{body}\n=======================\n")


def generate_unique_filename(original_filename):
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{ext}"


def upload2bucket(file_path, original_filename=None):
    bucket_name = "lamoda"
    if original_filename:
        unique_filename = generate_unique_filename(original_filename)
    else:
        unique_filename = os.path.basename(file_path)

    try:
        s3.upload_file(file_path, bucket_name, unique_filename)
        url = generate_presigned_url(bucket_name, unique_filename)
        return url
    except Exception as e:
        return None


def get_prompt():
    with open('prompt.txt') as file:
        return file.read()
