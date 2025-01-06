import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

S3_BUCKET_NAME = 'image-bucket-madhu'
DYNAMODB_TABLE_NAME = 'images-metadata'
REGION_NAME = 'ap-south-1'

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3', region_name=REGION_NAME)

def get_image_metadata(image_id):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    try:
        response = table.get_item(
            Key={'image_id': image_id}
        )
        return response.get('Item', None)

    except ClientError as e:
        raise Exception(f"Error retrieving metadata from DynamoDB: {str(e)}")

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': object_name},
                                             ExpiresIn=expiration)
        return response
    except ClientError as e:
        raise Exception(f"Error generating pre-signed URL: {str(e)}")

def lambda_handler(event, context):
    try:
        path_params = event.get('pathParameters', {})
        image_id = path_params.get('image_id', None)

        if not image_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'image_id is required'})
            }

        image_metadata = get_image_metadata(image_id)

        if not image_metadata:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Image not found'})
            }

        s3_key = f'{image_id}.jpg'
        presigned_url = generate_presigned_url(S3_BUCKET_NAME, s3_key)

        # Respond with the pre-signed URL for image download
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image found',
                'image_id': image_id,
                'download_url': presigned_url
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }