import boto3
import json
import gzip
from dotenv import load_dotenv
import os

# python-dotenv, bot3

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_PASSWORD")

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


bucket_name = 'ooni-data-eu-fra'

response = s3.list_objects_v2(Bucket=bucket_name)

file_count = 0
for obj in response.get('Contents', []):
    print(obj['Key'])
    file_count += 1
    if file_count >= 10:
        break
