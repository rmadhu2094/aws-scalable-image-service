import json
import boto3
from botocore.exceptions import ClientError

S3_BUCKET_NAME = 'image-bucket-madhu'
DYNAMODB_TABLE_NAME = 'images-metadata'

# Initialize DynamoDB and S3 clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# get image metadata from DynamoDB by image_id
def get_image_metadata(image_id):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    try:
        # Query DynamoDB to get the metadata for the specified image_id
        response = table.get_item(
            Key={'image_id': image_id}
        )
        return response.get('Item', None)

    except ClientError as e:
        raise Exception(f"Error retrieving metadata from DynamoDB: {str(e)}")

# Helper function to delete image from S3
def delete_image_from_s3(image_key):
    try:
        # Delete the image from S3 using the image key
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=image_key)
        return True
    except ClientError as e:
        raise Exception(f"Error deleting image from S3: {str(e)}")

# Helper function to delete image metadata from DynamoDB
def delete_image_metadata_from_dynamodb(image_id):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    try:
        # Delete the image metadata from DynamoDB
        response = table.delete_item(
            Key={'image_id': image_id}
        )
        return response
    except ClientError as e:
        raise Exception(f"Error deleting metadata from DynamoDB: {str(e)}")

# Lambda handler to delete image
def lambda_handler(event, context):
    try:
        # Extract the image_id from the path parameters
        path_params = event.get('pathParameters', {})
        image_id = path_params.get('image_id', None)

        if not image_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'image_id is required'})
            }

        # Retrieve the image metadata from DynamoDB
        image_metadata = get_image_metadata(image_id)

        if not image_metadata:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Image not found'})
            }

        # Get the S3 key 
        s3_key = f'{image_id}.jpg'

        # Delete the image metadata from DynamoDB
        delete_image_metadata_from_dynamodb(image_id)
        
        # Delete the image from S3
        delete_image_from_s3(s3_key)


        # Respond with a success message
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image deleted successfully',
                'image_id': image_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }