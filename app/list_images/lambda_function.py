import json
import boto3
from botocore.exceptions import ClientError

S3_BUCKET_NAME = 'image-bucket'
DYNAMODB_TABLE_NAME = 'images-metadata'

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Helper function to query DynamoDB with optional filters
def query_images(title=None, description=None, limit=10):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    filter_expression = []
    expression_values = {}

    # Build the filter expression based on provided filters
    if title:
        filter_expression.append('contains(title, :title)')
        expression_values[':title'] = title
    if description:
        filter_expression.append('contains(description, :description)')
        expression_values[':description'] = description

    # Join filters if both are provided
    filter_expression_str = ' and '.join(filter_expression) if filter_expression else None

    try:
        # Perform a scan query with filters if any
        response = table.scan(
            FilterExpression=filter_expression_str,
            ExpressionAttributeValues=expression_values,
            Limit=limit
        )
        return response['Items']

    except ClientError as e:
        raise Exception(f"Error querying DynamoDB: {str(e)}")

# Lambda handler to list images with filters
def lambda_handler(event, context):
    try:
        # Extract query parameters for filtering (title and description)
        query_params = event.get('queryStringParameters', {})
        title_filter = query_params.get('title', None)
        description_filter = query_params.get('description', None)
        limit = int(query_params.get('limit', 10))  # Default to 10 results if limit is not provided

        # Query DynamoDB for images
        images = query_images(title=title_filter, description=description_filter, limit=limit)

        # Prepare response with images metadata
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Images retrieved successfully',
                'images': images
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }