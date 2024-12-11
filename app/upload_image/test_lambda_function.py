import unittest
from unittest.mock import patch, MagicMock
import json
import base64
from lambda_function import lambda_handler

class TestUploadImageLambdaHandler(unittest.TestCase):

    @patch('lambda_function.upload_to_s3')
    @patch('lambda_function.save_metadata_to_dynamodb')
    def test_lambda_handler_success(self, mock_save_metadata_to_dynamodb, mock_upload_to_s3):
        mock_upload_to_s3.return_value = 'test-image.jpg'
        mock_save_metadata_to_dynamodb.return_value = None

        dummy_image_data = base64.b64encode(b"dummy image data").decode('utf-8')

        event = {
            'body': json.dumps({
                'image_file': dummy_image_data,
                'title': 'Test Image',
                'description': 'Test Description'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Image uploaded successfully')
        self.assertIn('image_id', body)

    @patch('lambda_function.upload_to_s3')
    @patch('lambda_function.save_metadata_to_dynamodb')
    def test_lambda_handler_missing_fields(self, mock_save_metadata_to_dynamodb, mock_upload_to_s3):
        event = {
            'body': json.dumps({
                'image_file': '',
                'title': 'Test Image'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Image file, title, and description are required')

    @patch('lambda_function.upload_to_s3')
    #@patch('lambda_function.save_metadata_to_dynamodb')
    def test_lambda_handler_upload_failure(self,mock_upload_to_s3):
        mock_upload_to_s3.side_effect = Exception('S3 upload error')

        dummy_image_data = base64.b64encode(b"dummy image data").decode('utf-8')

        event = {
            'body': json.dumps({
                'image_file': dummy_image_data,
                'title': 'Test Image',
                'description': 'Test Description'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'S3 upload error')

    @patch('lambda_function.upload_to_s3')
    @patch('lambda_function.save_metadata_to_dynamodb')
    def test_lambda_handler_metadata_save_failure(self, mock_save_metadata_to_dynamodb, mock_upload_to_s3):
        mock_upload_to_s3.return_value = 'test-image.jpg'

        mock_save_metadata_to_dynamodb.side_effect = Exception('DynamoDB error')

        dummy_image_data = base64.b64encode(b"dummy image data").decode('utf-8')

        event = {
            'body': json.dumps({
                'image_file': dummy_image_data,
                'title': 'Test Image',
                'description': 'Test Description'
            })
        }

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'DynamoDB error')

if __name__ == '__main__':
    unittest.main()
