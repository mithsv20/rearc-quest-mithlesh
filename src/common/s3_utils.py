import boto3
from common.config import AWS_REGION

def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)

def upload_text(bucket, key, body):
    s3 = get_s3_client()
    s3.put_object(Bucket=bucket, Key=key, Body=body)

def list_keys(bucket, prefix):
    s3 = get_s3_client()
    paginator = s3.get_paginator("list_objects_v2")

    keys = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys
