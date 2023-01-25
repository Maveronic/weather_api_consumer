import mock
from django.test import TestCase, Client
from django.urls import reverse
from decouple import config
from weather_API.views import weather
import datetime
import json
import requests

class WeatherViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.valid_payload = {'city': 'Lagos'}
        self.invalid_payload = {'city': ''}
        self.API_KEY = config('WEATHER_API_KEY')

    def test_weather_view_valid_payload(self):
        response = self.client.post(
            reverse('weather'),
            data=self.valid_payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data['temperature']['celsius'], float)
        self.assertIsInstance(response.data['temperature']['fahrenheit'], float)
        self.assertIsInstance(response.data['feels_like']['celsius'], float)
        self.assertIsInstance(response.data['feels_like']['fahrenheit'], float)
        self.assertIsInstance(response.data['humidity'], int)
        self.assertIsInstance(response.data['wind_speed'], float)
        self.assertIsInstance(response.data['description'], str)
        self.assertIsInstance(response.data['sunrise_time'], datetime.datetime)
        self.assertIsInstance(response.data['sunset_time'], datetime.datetime)

    def test_weather_view_invalid_payload(self):
        response = self.client.post(
            reverse('weather'),
            data=self.invalid_payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid city name')
        
    def test_weather_view_missing_city_key(self):
        payload = {} # payload is empty
        response = self.client.post(reverse('weather'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'error': 'city key not found in payload'})
        
    def test_weather_view_request_error(self):
        """
        Test that the view returns a 400 status code and an error message when a request exception is raised
        """
        payload = {'city': 'Lagos'}
        with mock.patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException('Error connecting to the server')
            response = self.client.post(reverse('weather'), data=json.dumps(payload), content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['error'], 'Error connecting to the server')

    def test_weather_view_key_error(self):
        """
        Test that the view returns a 400 status code and an error message when a key error is raised
        """
        payload = {'city': 'InvalidCity'}
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'cod': '404', 'message': 'city not found'}
            response = self.client.post(reverse('weather'), data=json.dumps(payload), content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['error'], 'Invalid city name')
