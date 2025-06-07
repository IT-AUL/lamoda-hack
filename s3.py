import boto3


def s3service():
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id='YCAJEvAsqxlrnUYdC-xtHzsWu',
        aws_secret_access_key='YCNC-cxCnXbMYPQ7MVhZUNe9gnr3x9FUjMDJVUa8'
    )
    return s3
