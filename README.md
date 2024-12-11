# aws-scalable-image-service

## Overview
This service allows users to:

1. Upload images (to a local S3 bucket) along with their metadata (stored in a local DynamoDB table).
2. List all images with filtering support.
3. View/download images via pre-signed URLs.
4. Delete images from the S3 bucket and metadat from DynamoDB table.

Note: The infrastructure uses LocalStack to simulate AWS services locally.

## Prerequisites:

1. Docker (to run LocalStack).
2. AWS CLI (configured to interact with LocalStack).
3. LocalStack CLI.
4. Python 3.7+ (with boto3 installed).

## API Endpoints

Lambda functions can be called using API Gateway (LocalStack resource).

### Upload Image
    Method: POST
    Endpoint: /upload
    Lambda: upload_image
    payload description: body - A JSON string containing the actual data for the image and its metadata.
        Includes:
            1. image_file: A base64-encoded string representing the image file to be uploaded.
            2. title: A short, descriptive title for the image.
            3. description: A brief explanation or description of the image.
    payload sample: 
        "body": "{\"image_file\": \"iVBORw0KGgoAAAANSUhEUgAAAAUA...\", \"title\": \"Sample Image\", \"description\": \"This is a description of the sample image.\"}"

### List Images
    Method: GET
    Endpoint: /images
    Lambda: list_images
    payload description: queryStringParameters: Encoded as a JSON string
        Includes:
            1. title: The title of the image
            2. description: A description of the image (optional)
            3. limit: Specifies the maximum number of results to be returned
    payload sample: 
    {"queryStringParameters": "{\"title\": \"Sample Image\", \"description\": \"sample description\", \"limit\": \"5\"}"}

### View/Download Image
    Method: GET
    Endpoint: /image/{image_id}
    Lambda: view_images
    payload description: This payload contains a single key, pathParameters
        Includes:
            1. image_id: The unique identifier of the image
           
    payload sample: 
    {"pathParameters": "{\"image_id\": \"d6a2a982-9839-4139-a827-7886ebed31\"}"}

### Delete Image
    Method: DELETE
    Endpoint: /image/{image_id}
    Lambda: delete_images
    payload description: This payload contains a single key, pathParameters
        Includes:
            1. image_id: The unique identifier of the image
           
    payload sample: 
    {"pathParameters": "{\"image_id\": \"d6a2a982-9839-4139-a827-7886ebed31\"}"}


   