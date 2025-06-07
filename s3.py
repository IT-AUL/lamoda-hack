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


def generate_presigned_url(bucket_name, object_name, expiration=3600):
    s3 = s3service()
    try:
        response = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )
        return response
    except Exception as e:
        return None
