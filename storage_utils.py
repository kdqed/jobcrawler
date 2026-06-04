from io import BytesIO

import boto3
from botocore.exceptions import ClientError
import niquests

import config


s3_client = boto3.client(
    's3',
    endpoint_url = 'https://' + config.S3_ENDPOINT,
    aws_access_key_id = config.S3_ACCESS_KEY,
    aws_secret_access_key = config.S3_SECRET_KEY,
)


from io import BytesIO
from PIL import Image

def _resize_image_bytes(image_data, max_pixels):
    image_data.seek(0)
    
    with Image.open(image_data) as img:
        img.thumbnail((max_pixels, max_pixels), Image.Resampling.LANCZOS)
        
        resized_io = BytesIO()
        img.save(resized_io, format='PNG')
        
        resized_io.seek(0)
        
        return resized_io


def key_exists(obj_key):
    try:
        s3_client.head_object(
            Bucket = config.S3_BUCKET, 
            Key = f'{config.ENV_TYPE}/{obj_key}'
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        raise e

        
def get_last_mod(obj_key):
    try:
        response = s3_client.head_object(
            Bucket = config.S3_BUCKET,
            Key = f'{config.ENV_TYPE}/{obj_key}',
        )
        return response['LastModified'].astimezone(None).replace(tzinfo=None)
    except Exception as e:
        return datetime(1970, 1, 1)


def upload_org_logo(url, obj_key):
    response = niquests.get(url, stream=True)
    
    if response.status_code != 200:
        return
    
    image_data = BytesIO(response.content)
    image_data = _resize_image_bytes(image_data, 192)
    
    extra_args = {
        "ContentType": 'image/png',
        "ACL": 'public-read',
    }
    
    try:
        s3_client.upload_fileobj(
            Fileobj = image_data,
            Bucket = config.S3_BUCKET,
            Key = f'{config.ENV_TYPE}/{obj_key}',
            ExtraArgs = extra_args or None,
        )
    except Exception as e:
        pass


def get_temp_access_url(key, seconds=60):
    url = s3_client.generate_presigned_url(
        ClientMethod = 'get_object',
        Params = {
            'Bucket': config.S3_BUCKET,
            'Key': f'{config.ENV_TYPE}/{key}',
            'ResponseContentType': 'application/pdf',
            'ResponseContentDisposition': 'inline',
        },
        ExpiresIn = seconds,
    )
    return url

        
def upload_resume(filepath, filename):
    s3_client.upload_file(
        Filename = filepath,
        Bucket = config.S3_BUCKET,
        Key = f'{config.ENV_TYPE}/resumes/{filename}',
    )

    
def upload_custom_resume(filepath, filename):
    s3_client.upload_file(
        Filename = filepath,
        Bucket = config.S3_BUCKET,
        Key = f'{config.ENV_TYPE}/custom_resumes/{filename}',
    )
