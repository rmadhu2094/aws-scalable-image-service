import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler, query_images

class TestLambdaHandler(unittest.TestCase):

    @patch('lambda_function.query_images')
    def test_list_images_no_filters(self, mock_query_images):
        mock_query_images.return_value = [
            {'image_id': '1', 'title': 'Sunset', 'description': 'A beautiful sunset'},
            {'image_id': '2', 'title': 'Mountain', 'description': 'A scenic mountain view'}
        ]
        event = {
            'queryStringParameters': {}
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Images retrieved successfully')
        self.assertEqual(len(body['images']), 2)

    @patch('lambda_function.query_images')
    def test_list_images_with_filters(self, mock_query_images):
        mock_query_images.return_value = [
            {'image_id': '1', 'title': 'Sunset', 'description': 'A beautiful sunset'}
        ]
        event = {
            'queryStringParameters': {
                'title': 'Sunset',
                'limit': '5'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Images retrieved successfully')
        self.assertEqual(len(body['images']), 1)

    @patch('lambda_function.query_images')
    def test_list_images_empty_result(self, mock_query_images):
        mock_query_images.return_value = []
        event = {
            'queryStringParameters': {
                'description': 'Nonexistent',
                'limit': '5'
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Images retrieved successfully')
        self.assertEqual(len(body['images']), 0)

    @patch('lambda_function.query_images')
    def test_list_images_exception_handling(self, mock_query_images):
        mock_query_images.side_effect = Exception('Database error')
        event = {
            'queryStringParameters': {}
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Database error')

if __name__ == '__main__':
    unittest.main()
