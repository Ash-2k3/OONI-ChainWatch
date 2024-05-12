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

def download_and_parse_measurement(bucket_name, object_key):
           """Downloads and parses a single measurement from S3."""
           try: 
                      obj = s3.get_object(Bucket=bucket_name, Key=object_key)
                      with gzip.GzipFile(fileobj=obj['Body']) as gzip_file:
                                 measurement_data = json.load(gzip_file)
                      return measurement_data
           except Exception as e:
                      print(f"Error downloading or parsing file {object_key}: {e}")

file_count = 0
for obj in response.get('Contents', []):
    file_key = obj['Key']
    # Check if the file is gzipped and in json convertible format.
    if file_key.endswith('.json.gz'):
        print('*************************************')
        print(obj['Key'])
        try:
            # Download and parse the measurement data
            measurement_data = download_and_parse_measurement(bucket_name, obj['Key'])
            print(measurement_data)
        except Exception as e:
            print(f"Error processing file {file_key}: {e}")
        file_count += 1
        if file_count >= 10:
            break
    else:
        print(f"Skipping non-gzipped file: {file_key}")
