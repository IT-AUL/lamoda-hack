import random
import string

import boto3

from s3 import s3service

s3 = s3service()

def generate_random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_username(email):
    base = email.split('@')[0]
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{base}_{suffix}"


def send_email_mock(to, subject, body):
    print(f"\n=== Email to: {to} ===\nSubject: {subject}\n{body}\n=======================\n")

def upload2bucket(file_path):
    bucket_name = "lamoda"
    s3.upload_file(file_path, bucket_name, file_path)
