# In a new file utils/storage.py
import boto3
import os
from botocore.exceptions import ClientError
from flask import current_app

def upload_file_to_s3(file_data, bucket_name, object_name=None):
    """Upload a file to an S3 bucket"""
    if object_name is None:
        object_name = file_data.filename
    
    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file_data, bucket_name, object_name)
    except ClientError as e:
        current_app.logger.error(e)
        return False
    return True

def get_s3_url(bucket_name, object_name):
    """Generate a URL for the uploaded file"""
    return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"