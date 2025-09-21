"""
Weather8 Integration Tests
Tests Flask app endpoints, caching system, and end-to-end functionality.
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask app and components
from app import app, cache, get_cached_data, set_cache_data, is_cache_valid
from models import WeatherData, WeatherForecast, Location, CurrentWeather, ForecastDay


class TestFlaskApp(unittest.TestCase):
    """Integration tests for Flask application endpoints"""
    
    def setUp(self):
        """Set up test client and mock data"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear cache before each test
        cache.clear()
        
        # Mock weather data for consistent testing
        self.mock_current_response = {
            'location': {
                'name': 'Test City',
                'country': 'Test Country',
                'region': 'Test Region',
                'localtime': '2024-01-01 12:00'
            },
            'current': {
                'temp_c': 25.0,
                'temp_f': 77.0,
                'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
                'humidity': 60,
                'wind_kph': 10.0,
                'wind_dir': 'N',
                'feelslike_c': 27.0,
                'uv': 5.0,
                'vis_km': 15.0,
                'last_updated': '2024-01-01 12:00'
            }
        }
        
        self.mock_forecast_response = {
            'location': {
                'name': 'Test City',
                'country': 'Test Country',
                'region': 'Test Region'
            },
            'forecast': {
                'forecastday': [
                    {
                        'date': '2024-01-01',
                        'day': {
                            'maxtemp_c': 28.0,
                            'mintemp_c': 18.0,
                            'maxtemp_f': 82.4,
                            'mintemp_f': 64.4,
                            'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
                            'daily_chance_of_rain': 0,
                            'avghumidity': 55
                        }
                    },
                    {
                        'date': '2024-01-02',
                        'day': {
                            'maxtemp_c': 30.0,
                            'mintemp_c': 20.0,
                            'maxtemp_f': 86.0,
                            'mintemp_f': 68.0,
                            'condition': {'text': 'Partly Cloudy', 'icon': '//cloudy.png'},
                            'daily_chance_of_rain': 20,
                            'avghumidity': 65
                        }
                    }
                ]
            }
        }
    
    def test_index_route(self):
        """Test main dashboard route returns HTML"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Weather8', response.data)
        self.assertIn(b'search', response.data.lower())
    
    def test_current_weather_missing_city(self):
        """Test current weather endpoint without city parameter"""
        response = self.app.get('/api/weather/current')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('City parameter is required', data['error'])
    
    def test_current_weather_empty_city(self):
        """Test current weather endpoint with empty city"""
        response = self.app.get('/api/weather/current?city=')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('City parameter is required', data['error'])
    
    @patch('app.weather_client')
    def test_current_weather_success(self, mock_client):
        """Test successful current weather API call"""
        mock_client.get_current_weather.return_value = self.mock_current_response
        
        response = self.app.get('/api/weather/current?city=TestCity')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertFalse(data['cached'])  # First call should not be cached
        self.assertEqual(data['data']['location']['name'], 'Test City')
        self.assertEqual(data['data']['current']['temperature_c'], 25.0)
    
    @patch('app.weather_client')
    def test_forecast_success(self, mock_client):
        """Test successful forecast API call"""
        mock_client.get_forecast.return_value = self.mock_forecast_response
        
        response = self.app.get('/api/weather/forecast?city=TestCity')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertFalse(data['cached'])
        self.assertEqual(len(data['data']['forecast']), 2)
        self.assertEqual(data['data']['forecast'][0]['max_temp_c'], 28.0)
    
    @patch('app.weather_client')
    def test_city_not_found_error(self, mock_client):
        """Test city not found error handling"""
        from weather_client import CityNotFoundError
        mock_client.get_current_weather.side_effect = CityNotFoundError("City 'InvalidCity' not found")
        
        response = self.app.get('/api/weather/current?city=InvalidCity')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'])
    
    @patch('app.weather_client')
    def test_network_error_handling(self, mock_client):
        """Test network error handling"""
        from weather_client import NetworkError
        mock_client.get_current_weather.side_effect = NetworkError("Network timeout")
        
        response = self.app.get('/api/weather/current?city=TestCity')
        self.assertEqual(response.status_code, 503)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('connect to weather service', data['error'])
    
    @patch('app.weather_client')
    def test_api_key_error_handling(self, mock_client):
        """Test API key error handling"""
        from weather_client import APIKeyError
        mock_client.get_current_weather.side_effect = APIKeyError("Invalid API key")
        
        response = self.app.get('/api/weather/current?city=TestCity')
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('authentication error', data['error'])
    
    def test_cache_status_endpoint(self):
        """Test cache status debugging endpoint"""
        response = self.app.get('/api/cache/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('cache_entries', data)
        self.assertIn('cache_duration_minutes', data)
        self.assertEqual(data['cache_entries'], 0)  # Should start empty


class TestCachingSystem(unittest.TestCase):
    """Test cases for the caching system"""
    
    def setUp(self):
        """Clear cache before each test"""
        cache.clear()
    
    def test_cache_storage_and_retrieval(self):
        """Test basic cache storage and retrieval"""
        test_data = {'temperature': 25, 'condition': 'Sunny'}
        cache_key = 'test_city'
        
        # Store data in cache
        set_cache_data(cache_key, test_data)
        
        # Retrieve data from cache
        cached_data = get_cached_data(cache_key)
        
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['temperature'], 25)
        self.assertEqual(cached_data['condition'], 'Sunny')
    
    def test_cache_expiration(self):
        """Test that cache expires after TTL"""
        test_data = {'temperature': 25}
        cache_key = 'test_expiry'
        
        # Manually set cache with old timestamp
        old_timestamp = datetime.now() - timedelta(minutes=15)
        cache[cache_key] = (test_data, old_timestamp)
        
        # Should return None for expired data
        cached_data = get_cached_data(cache_key)
        self.assertIsNone(cached_data)
    
    def test_cache_validity_check(self):
        """Test cache validity checking function"""
        # Valid timestamp (within TTL)
        valid_timestamp = datetime.now() - timedelta(minutes=5)
        self.assertTrue(is_cache_valid(valid_timestamp))
        
        # Invalid timestamp (beyond TTL)
        invalid_timestamp = datetime.now() - timedelta(minutes=15)
        self.assertFalse(is_cache_valid(invalid_timestamp))
    
    def test_multiple_cache_keys(self):
        """Test multiple cache keys don't interfere"""
        data1 = {'city': 'Lagos', 'temp': 30}
        data2 = {'city': 'London', 'temp': 15}
        
        set_cache_data('lagos', data1)
        set_cache_data('london', data2)
        
        # Both should be retrievable
        lagos_data = get_cached_data('lagos')
        london_data = get_cached_data('london')
        
        self.assertEqual(lagos_data['city'], 'Lagos')
        self.assertEqual(london_data['city'], 'London')
        self.assertEqual(lagos_data['temp'], 30)
        self.assertEqual(london_data['temp'], 15)


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        cache.clear()
    
    @patch('app.weather_client')
    def test_complete_weather_workflow(self, mock_client):
        """Test complete weather search workflow"""
        # Mock API responses
        mock_current = {
            'location': {'name': 'Lagos', 'country': 'Nigeria', 'region': 'Lagos'},
            'current': {
                'temp_c': 28.0, 'temp_f': 82.4,
                'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
                'humidity': 65, 'wind_kph': 15.0, 'wind_dir': 'SW',
                'feelslike_c': 30.0, 'uv': 7.0, 'vis_km': 10.0,
                'last_updated': '2024-01-01 12:00'
            }
        }
        
        mock_forecast = {
            'location': {'name': 'Lagos', 'country': 'Nigeria'},
            'forecast': {
                'forecastday': [
                    {
                        'date': '2024-01-01',
                        'day': {
                            'maxtemp_c': 30.0, 'mintemp_c': 22.0,
                            'maxtemp_f': 86.0, 'mintemp_f': 71.6,
                            'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
                            'daily_chance_of_rain': 5, 'avghumidity': 60
                        }
                    }
                ]
            }
        }
        
        mock_client.get_current_weather.return_value = mock_current
        mock_client.get_forecast.return_value = mock_forecast
        
        # Step 1: Get current weather
        current_response = self.app.get('/api/weather/current?city=Lagos')
        self.assertEqual(current_response.status_code, 200)
        
        current_data = json.loads(current_response.data)
        self.assertTrue(current_data['success'])
        self.assertEqual(current_data['data']['location']['name'], 'Lagos')
        
        # Step 2: Get forecast
        forecast_response = self.app.get('/api/weather/forecast?city=Lagos')
        self.assertEqual(forecast_response.status_code, 200)
        
        forecast_data = json.loads(forecast_response.data)
        self.assertTrue(forecast_data['success'])
        self.assertEqual(len(forecast_data['data']['forecast']), 1)
        
        # Step 3: Test caching - second request should be cached
        current_response_2 = self.app.get('/api/weather/current?city=Lagos')
        current_data_2 = json.loads(current_response_2.data)
        self.assertTrue(current_data_2['cached'])
    
    @patch('app.weather_client')
    def test_error_recovery_workflow(self, mock_client):
        """Test error handling and recovery"""
        from weather_client import CityNotFoundError, NetworkError
        
        # First request - city not found
        mock_client.get_current_weather.side_effect = CityNotFoundError("City not found")
        response1 = self.app.get('/api/weather/current?city=InvalidCity')
        self.assertEqual(response1.status_code, 404)
        
        # Second request - network error
        mock_client.get_current_weather.side_effect = NetworkError("Network timeout")
        response2 = self.app.get('/api/weather/current?city=TestCity')
        self.assertEqual(response2.status_code, 503)
        
        # Third request - success (recovery)
        mock_client.get_current_weather.side_effect = None
        mock_client.get_current_weather.return_value = {
            'location': {'name': 'Lagos', 'country': 'Nigeria'},
            'current': {'temp_c': 28.0, 'condition': {'text': 'Sunny'}}
        }
        response3 = self.app.get('/api/weather/current?city=Lagos')
        self.assertEqual(response3.status_code, 200)


class TestDataValidation(unittest.TestCase):
    """Test data validation and sanitization"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_city_name_sanitization(self):
        """Test that city names are properly sanitized"""
        # Test with extra whitespace
        response1 = self.app.get('/api/weather/current?city=  Lagos  ')
        # Should not fail due to whitespace (handled by strip())
        self.assertIn(response1.status_code, [200, 404, 503])  # Valid HTTP responses
        
        # Test with special characters
        response2 = self.app.get('/api/weather/current?city=São Paulo')
        self.assertIn(response2.status_code, [200, 404, 503])
    
    def test_url_encoding_handling(self):
        """Test URL encoding is handled properly"""
        # Test with URL encoded city name
        response = self.app.get('/api/weather/current?city=New%20York')
        self.assertIn(response.status_code, [200, 404, 503])


class TestErrorPages(unittest.TestCase):
    """Test custom error page handling"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_404_page(self):
        """Test custom 404 error page"""
        response = self.app.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
    
    def test_405_method_not_allowed(self):
        """Test method not allowed on API endpoints"""
        # POST to GET-only endpoint
        response = self.app.post('/api/weather/current')
        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=True)