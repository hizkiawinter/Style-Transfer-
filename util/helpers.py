import boto3, botocore 
import os 
from werkzeug.utils import secure_filename 

s3 = boto3.client(
    service_name = "s3", 
    aws_access_key_id = '[AWS ACCESS KEY]', 
    aws_secret_access_key = "[AWS SECRET KEY]",
    region_name = "ap-southeast-1"
)

def upload_file_to_s3(file, acl = "public-read"):
    filename =secure_filename(file.filename)
    try:
        s3.upload_fileobj(
            file, 
            'runpod-hizkia-fileupload', 
            file.filename, 
            ExtraArgs = {
                "ACL": acl, 
                "ContentType": file.content_type, 
            }
        )
    except Exception as e: 
        print('Something Happened: ', e)
        print("File:", file)
        print("Filename:", filename)
        print("Content Type:", file.content_type)
        return e 
    
    return file.filename