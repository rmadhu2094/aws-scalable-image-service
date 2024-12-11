import unittest
from unittest.mock import patch, MagicMock
import json
from botocore.exceptions import ClientError

from lambda_function import lambda_handler


class TestImageUpload(unittest.TestCase):

    @patch('boto3.client')
    @patch('boto3.resource')
    def test_upload_image_success(self, mock_dynamodb, mock_s3):
        # Mock S3 client and DynamoDB resource
        mock_s3_client = MagicMock()
        mock_s3.return_value = mock_s3_client
        mock_dynamodb_resource = MagicMock()
        mock_dynamodb.return_value = mock_dynamodb_resource

        # Mock DynamoDB Table
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table

        # Mock the image metadata insertion into DynamoDB
        mock_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Mock S3 upload
        mock_s3_client.upload_fileobj.return_value = None

        event = {
            'body': json.dumps({
                'image_id': '12345-abcde',
                'image_name': 'sample.jpg',
                'user_id': 'user123',
                'tags': ['tag1', 'tag2']
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

        context = {}

        response = lambda_handler(event, context)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('image_id', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], 'Image uploaded successfully')

    @patch('boto3.client')
    @patch('boto3.resource')
    def test_upload_image_missing_metadata(self, mock_dynamodb, mock_s3):
        # Mock S3 client and DynamoDB resource
        mock_s3_client = MagicMock()
        mock_s3.return_value = mock_s3_client
        mock_dynamodb_resource = MagicMock()
        mock_dynamodb.return_value = mock_dynamodb_resource

        # Mock DynamoDB Table
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table

        event = {
            'body': json.dumps({
                'image_id': '12345-abcde',
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

        context = {}

        response = lambda_handler(event, context)

        # Assertions
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('message', json.loads(response['body']))
        self.assertEqual(json.loads(response['body'])['message'], 'Metadata missing')

    @patch('boto3.client')
    @patch('boto3.resource')
    def test_upload_image_s3_failure(self, mock_dynamodb, mock_s3):
        # Mock S3 client and DynamoDB resource
        mock_s3_client = MagicMock()
        mock_s3.return_value = mock_s3_client
        mock_dynamodb_resource = MagicMock()
        mock_dynamodb.return_value = mock_dynamodb_resource

        # Mock DynamoDB Table
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table

        mock_s3_client.upload_fileobj.side_effect = ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'Upload')

        event = {
            'body': json.dumps({
                'image_id': '12345-abcde',
                'image_name': 'sample.jpg',
                'user_id': 'user123',
                'tags': ['tag1', 'tag2']
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

        context = {}
        response = lambda_handler(event, context)

        # Assertions
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('message', json.loads(response['body']))
        self.assertTrue('Error uploading image to S3' in json.loads(response['body'])['message'])


if __name__ == '__main__':
    unittest.main()