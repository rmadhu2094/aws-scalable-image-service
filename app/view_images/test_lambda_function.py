import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('lambda_function.get_image_metadata')
    @patch('lambda_function.generate_presigned_url')
    def test_valid_image_id(self, mock_generate_presigned_url, mock_get_image_metadata):
        # Mock metadata and presigned URL
        mock_get_image_metadata.return_value = {
            'image_id': '12345',
            's3_url': 'https://image_bucket.s3.amazonaws.com/some_image_key.jpg'
        }
        mock_generate_presigned_url.return_value = 'https://presigned-url.com'

        # Mock event
        event = {
            'pathParameters': {
                'image_id': '12345'
            }
        }

        # Call lambda_handler
        response = lambda_handler(event, None)

        # Validate response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Image found')
        self.assertEqual(body['image_id'], '12345')
        self.assertEqual(body['download_url'], 'https://presigned-url.com')

    @patch('lambda_function.get_image_metadata')
    def test_missing_image_id(self, mock_get_image_metadata):
        # Mock event without image_id
        event = {
            'pathParameters': {}
        }

        # Call lambda_handler
        response = lambda_handler(event, None)

        # Validate response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'image_id is required')

    @patch('lambda_function.get_image_metadata')
    def test_image_not_found(self, mock_get_image_metadata):
        # Mock no metadata found
        mock_get_image_metadata.return_value = None

        # Mock event
        event = {
            'pathParameters': {
                'image_id': '12345'
            }
        }

        # Call lambda_handler
        response = lambda_handler(event, None)

        # Validate response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Image not found')

    @patch('lambda_function.get_image_metadata')
    def test_exception_handling(self, mock_get_image_metadata):
        # Mock metadata retrieval to raise an exception
        mock_get_image_metadata.side_effect = Exception('Database error')

        # Mock event
        event = {
            'pathParameters': {
                'image_id': '12345'
            }
        }

        # Call lambda_handler
        response = lambda_handler(event, None)

        # Validate response
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Database error')


if __name__ == '__main__':
    unittest.main()