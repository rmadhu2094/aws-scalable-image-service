import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler, get_image_metadata, delete_image_from_s3, delete_image_metadata_from_dynamodb

S3_BUCKET_NAME = 'image_bucket'

class TestDeleteImageLambdaHandler(unittest.TestCase):

    @patch('lambda_function.get_image_metadata')
    @patch('lambda_function.delete_image_from_s3')
    @patch('lambda_function.delete_image_metadata_from_dynamodb')
    def test_delete_image_success(self, mock_delete_metadata, mock_delete_s3, mock_get_metadata):
        mock_get_metadata.return_value = {
            'image_id': '123',
            's3_url': f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/test_image.jpg'
        }
        mock_delete_s3.return_value = True
        mock_delete_metadata.return_value = {}
        event = {
            'pathParameters': {
                'image_id': '123'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Image deleted successfully')
        self.assertEqual(body['image_id'], '123')

    @patch('lambda_function.get_image_metadata')
    def test_delete_image_not_found(self, mock_get_metadata):
        mock_get_metadata.return_value = None
        event = {
            'pathParameters': {
                'image_id': '999'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Image not found')

    def test_delete_image_missing_image_id(self):
        event = {
            'pathParameters': {}
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'image_id is required')

    @patch('lambda_function.get_image_metadata')
    @patch('lambda_function.delete_image_from_s3')
    @patch('lambda_function.delete_image_metadata_from_dynamodb')
    def test_delete_image_error_handling(self, mock_delete_metadata, mock_delete_s3, mock_get_metadata):
        mock_get_metadata.return_value = {
            'image_id': '123',
            's3_url': f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/test_image.jpg'
        }
        mock_delete_s3.side_effect = Exception('S3 deletion failed')
        event = {
            'pathParameters': {
                'image_id': '123'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'S3 deletion failed')

if __name__ == '__main__':
    unittest.main()
