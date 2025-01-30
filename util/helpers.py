import boto3, botocore 
import os 
import io 
from werkzeug.utils import secure_filename 

s3 = boto3.client(
    service_name = "s3", 
    aws_access_key_id = 'AKIAS66UDDUB2NCV4PVI', 
    aws_secret_access_key = "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",
    region_name = "ap-southeast-1"
)

def get_file():
    response = s3.list_objects_v2(
        Bucket = 'runpod-hizkia-fileupload',
        Prefix = 'Output/'
    )

    return response 

def show_video(): 
    bucket = 'runpod-hizkia-fileupload'
    public_urls = [] 
    try:
        for item in s3.list_objects_v2(Bucket=bucket, Prefix='Input/Video_')['Contents']: 
            presigned_url = s3.generate_presigned_url('get_object', Params = {'Bucket':bucket, 'Key': item['Key']}, ExpiresIn = 100)
            public_urls.append(presigned_url)
    except Exception as e: 
        pass 

    return public_urls


def show_image():
    bucket = 'runpod-hizkia-fileupload' 
    public_urls = [] 
    try:
        for item in s3.list_objects_v2(Bucket=bucket, Prefix='Output/Frame_')['Contents']: 
            presigned_url = s3.generate_presigned_url('get_object', Params = {'Bucket':bucket, 'Key': item['Key']}, ExpiresIn = 100)
            public_urls.append(presigned_url)
    except Exception as e: 
        pass 

    return public_urls
    
    

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