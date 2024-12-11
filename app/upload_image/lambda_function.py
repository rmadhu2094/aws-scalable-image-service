import json
import boto3
import uuid
import base64
from botocore.exceptions import ClientError

S3_BUCKET_NAME = 'image-bucket'
DYNAMODB_TABLE_NAME = 'images-metadata'

s3 = boto3.client('s3',region_name='eu-west-1', endpoint_url='http://localhost:4566')
dynamodb = boto3.resource('dynamodb',region_name='eu-west-1', endpoint_url='http://localhost:4566')

def upload_to_s3(file_data, filename):
    try:
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=filename, Body=file_data)
        return filename
    except ClientError as e:
        raise Exception(f"Error uploading image to S3: {str(e)}")

def save_metadata_to_dynamodb(image_id, title, description, s3_url):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    try:
        table.put_item(
            Item={
                'image_id': image_id,
                'title': title,
                'description': description,
                's3_url': s3_url
            }
        )
    except ClientError as e:
        raise Exception(f"Error saving metadata to DynamoDB: {str(e)}")

def lambda_handler(event, context):
    try:
        # Extract the body and metadata from the incoming event
        body = json.loads(event['body'])
        image_file = body.get('image_file')
        title = body.get('title')
        description = body.get('description')

        if not image_file or not title or not description:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Image file, title, and description are required'})
            }

        image_id = str(uuid.uuid4())
        filename = f'{image_id}.jpg'

        decoded_image_data = base64.b64decode(image_file)
        s3_file_name = upload_to_s3(decoded_image_data, filename)

        s3_url = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{filename}'

        save_metadata_to_dynamodb(image_id, title, description, s3_url)

        # Respond with success
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Image uploaded successfully', 'image_id': image_id})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }