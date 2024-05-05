import unittest
import json
from unittest.mock import patch
from lambdas.dataset_aggregator.lambda_function import extract_event_data  # Adjust the import based on your actual script structure and name

class TestExtractEventData(unittest.TestCase):
    def test_extract_event_data(self):
        mock_record = {
            'body': json.dumps({
                'Records': [{
                    's3': {
                        'bucket': {
                            'name': 'test-bucket'
                        },
                        'object': {
                            'key': 'test-key.parquet',
                            'eTag': '123456789abcdef'
                        }
                    }
                }]
            })
        }

        # Expected result
        expected_result = {
            'bucket_name': 'test-bucket',
            'object_key': 'test-key.parquet',
            'object_etag': '123456789abcdef'
        }

        # Call the function with the mock data
        result = extract_event_data(mock_record)

        # Check if the result matches the expected result
        self.assertEqual(result, expected_result)

# Run the tests
if __name__ == '__main__':
    unittest.main()