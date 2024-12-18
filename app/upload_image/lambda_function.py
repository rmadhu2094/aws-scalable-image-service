import boto3
import json
import uuid
import base64

S3_BUCKET_NAME = 'image-bucket-madhu'
DYNAMODB_TABLE_NAME = 'images-metadata'

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def parse_multipart_formdata(body, content_type):
    """
    Parses a multipart/form-data payload manually.
    """
    # Extract the boundary from the Content-Type header
    boundary = content_type.split("boundary=")[1]
    boundary = f"--{boundary}"  # Prefix the boundary with "--"
    
    # Split the body into parts using the boundary
    parts = body.split(boundary.encode())

    form_data = {}
    for part in parts:
        if not part or part == b"--\r\n":  # Skip empty parts and closing boundary
            continue

        # Separate headers and content
        headers, content = part.split(b'\r\n\r\n', 1)
        content = content.rstrip(b'\r\n')  # Strip trailing CRLF

        # Decode headers
        headers = headers.decode('utf-8')
        
        # Check Content-Disposition header
        if 'Content-Disposition' in headers:
            # Extract the field name
            disposition = headers.split(';')
            name = None
            for item in disposition:
                if 'name=' in item:
                    name = item.split('=')[1].strip('"')
                    break
            
            # Check if this is a file field
            if 'filename=' in headers:
                form_data[name] = content  # Binary content of the file
            else:
                form_data[name] = content.decode('utf-8')  # Text content

    return form_data

def upload_to_s3(file_data, filename):
    try:
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=filename, Body=file_data)
        return filename
    except Exception as e:
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
    except Exception as e:
        raise Exception(f"Error saving metadata to DynamoDB: {str(e)}")

def lambda_handler(event, context):
    try:
        # Extract Content-Type and body
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        body = base64.b64decode(event['body'])  # Decode base64-encoded body from API Gateway

        # Parse form-data
        form_data = parse_multipart_formdata(body, content_type)

        # Extract form fields and file
        title = form_data.get('title')
        description = form_data.get('description')
        image_file = form_data.get('image_file')  # Binary content of the uploaded file

        if not title or not description or not image_file:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Image file, title, and description are required'})
            }

        # Generate a unique filename
        image_id = str(uuid.uuid4())
        filename = f'{image_id}.jpg'

        # Upload file to S3
        upload_to_s3(image_file, filename)

        # Generate S3 URL
        s3_url = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{filename}'

        # Save metadata to DynamoDB
        save_metadata_to_dynamodb(image_id, title, description, s3_url)

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image uploaded successfully',
                'image_id': image_id,
                's3_url': s3_url
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }
