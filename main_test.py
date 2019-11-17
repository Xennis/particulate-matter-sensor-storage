import unittest

from main import extract_sensor_data, RequestInvalidError


class TestExtractSensorData(unittest.TestCase):

    def test_valid(self):
        data = {
            'esp8266id': '9973235',
            'software_version': 'NRZ-2019-125-B1',
            'sensordatavalues': [
                {'value_type': 'SDS_P1', 'value': '11.03'},
                {'value_type': 'SDS_P2', 'value': '6.80'},
                {'value_type': 'temperature', 'value': '6.00'},
                {'value_type': 'humidity', 'value': '99.90'},
                {'value_type': 'samples', 'value': '2253523'},
                {'value_type': 'min_micro', 'value': '59'},
                {'value_type': 'max_micro', 'value': '26138'},
                {'value_type': 'signal', 'value': '-71'}
            ]
        }
        expected = {
            'humidity': 99.9,
            'max_micro': 26138.0,
            'min_micro': 59.0,
            'samples': 2253523.0,
            'sds_p1': 11.03,
            'sds_p2': 6.8,
            'signal': -71.0,
            'temperature': 6.0
        }
        actual = extract_sensor_data(data)
        self.assertEqual(expected, actual)

    def test_none_data(self):
        data = None
        self.assertRaises(RequestInvalidError, extract_sensor_data, data)

    def test_empty_data(self):
        data = {}
        self.assertRaises(RequestInvalidError, extract_sensor_data, data)

    def test_no_sensor_data(self):
        data = {
            'esp8266id': '9973235',
            'software_version': 'NRZ-2019-125-B1'
        }
        self.assertRaises(RequestInvalidError, extract_sensor_data, data)
