"""
Weather8 Unit Tests
Tests WeatherClient, domain models, and error handling.
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_client import (
    WeatherClient, WeatherAPIError, NetworkError, 
    CityNotFoundError, APIKeyError
)
from models import (
    Location, CurrentWeather, ForecastDay, WeatherData, 
    WeatherForecast, WeatherDataProcessor
)


class TestWeatherClient(unittest.TestCase):
    """Test cases for WeatherClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        with patch.dict(os.environ, {
            'WEATHER_API_KEY': 'test_api_key',
            'WEATHER_API_BASE_URL': 'http://test.api.com/v1'
        }):
            self.client = WeatherClient()
    
    def test_weather_client_initialization(self):
        """Test WeatherClient initializes correctly"""
        self.assertEqual(self.client.api_key, 'test_api_key')
        self.assertEqual(self.client.base_url, 'http://test.api.com/v1')
    
    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises APIKeyError"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(APIKeyError):
                WeatherClient()
    
    @patch('weather_client.requests.Session.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful weather API call"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'location': {
                'name': 'Lagos',
                'country': 'Nigeria',
                'region': 'Lagos'
            },
            'current': {
                'temp_c': 28.0,
                'temp_f': 82.4,
                'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
                'humidity': 65,
                'wind_kph': 15.0,
                'wind_dir': 'SW',
                'feelslike_c': 30.0,
                'uv': 7.0,
                'vis_km': 10.0,
                'last_updated': '2024-01-01 12:00'
            }
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_current_weather('Lagos')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['location']['name'], 'Lagos')
        self.assertEqual(result['current']['temp_c'], 28.0)
    
    @patch('weather_client.requests.Session.get')
    def test_city_not_found_error(self, mock_get):
        """Test CityNotFoundError is raised for invalid city"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        with self.assertRaises(CityNotFoundError):
            self.client.get_current_weather('InvalidCity123')
    
    @patch('weather_client.requests.Session.get')
    def test_api_key_error(self, mock_get):
        """Test APIKeyError is raised for invalid API key"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with self.assertRaises(APIKeyError):
            self.client.get_current_weather('Lagos')
    
    @patch('weather_client.requests.Session.get')
    def test_network_timeout_error(self, mock_get):
        """Test NetworkError is raised on timeout"""
        mock_get.side_effect = Exception("Timeout")
        
        with self.assertRaises(NetworkError):
            self.client.get_current_weather('Lagos')
    
    @patch('weather_client.requests.Session.get')
    def test_get_forecast_success(self, mock_get):
        """Test successful forecast API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'location': {'name': 'Lagos', 'country': 'Nigeria'},
            'forecast': {
                'forecastday': [
                    {
                        'date': '2024-01-01',
                        'day': {
                            'maxtemp_c': 30.0,
                            'mintemp_c': 22.0,
                            'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
                            'daily_chance_of_rain': 10,
                            'avghumidity': 60
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_forecast('Lagos')
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result['forecast']['forecastday']), 1)


class TestDomainModels(unittest.TestCase):
    """Test cases for domain model classes"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_location_data = {
            'name': 'Lagos',
            'country': 'Nigeria',
            'region': 'Lagos',
            'localtime': '2024-01-01 12:00'
        }
        
        self.sample_current_data = {
            'temp_c': 28.0,
            'temp_f': 82.4,
            'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
            'humidity': 65,
            'wind_kph': 15.0,
            'wind_dir': 'SW',
            'feelslike_c': 30.0,
            'uv': 7.0,
            'vis_km': 10.0,
            'last_updated': '2024-01-01 12:00'
        }
    
    def test_location_from_api_response(self):
        """Test Location creation from API response"""
        location = Location.from_api_response(self.sample_location_data)
        
        self.assertEqual(location.name, 'Lagos')
        self.assertEqual(location.country, 'Nigeria')
        self.assertEqual(location.region, 'Lagos')
    
    def test_current_weather_from_api_response(self):
        """Test CurrentWeather creation from API response"""
        weather = CurrentWeather.from_api_response(self.sample_current_data)
        
        self.assertEqual(weather.temperature_c, 28.0)
        self.assertEqual(weather.condition, 'Sunny')
        self.assertEqual(weather.humidity, 65)
    
    def test_current_weather_to_dict(self):
        """Test CurrentWeather to_dict conversion"""
        weather = CurrentWeather.from_api_response(self.sample_current_data)
        weather_dict = weather.to_dict()
        
        self.assertIsInstance(weather_dict, dict)
        self.assertEqual(weather_dict['temperature_c'], 28.0)
        self.assertEqual(weather_dict['condition'], 'Sunny')
    
    def test_forecast_day_from_api_response(self):
        """Test ForecastDay creation from API response"""
        day_data = {
            'date': '2024-01-01',
            'day': {
                'maxtemp_c': 30.0,
                'mintemp_c': 22.0,
                'condition': {'text': 'Sunny', 'icon': '//sunny.png'},
                'daily_chance_of_rain': 10,
                'avghumidity': 60
            }
        }
        
        forecast_day = ForecastDay.from_api_response(day_data)
        
        self.assertEqual(forecast_day.date, '2024-01-01')
        self.assertEqual(forecast_day.max_temp_c, 30.0)
        self.assertEqual(forecast_day.min_temp_c, 22.0)
    
    def test_weather_data_from_api_response(self):
        """Test WeatherData creation from complete API response"""
        api_data = {
            'location': self.sample_location_data,
            'current': self.sample_current_data
        }
        
        weather_data = WeatherData.from_api_response(api_data)
        
        self.assertEqual(weather_data.location.name, 'Lagos')
        self.assertEqual(weather_data.current.temperature_c, 28.0)


class TestWeatherDataProcessor(unittest.TestCase):
    """Test cases for WeatherDataProcessor utility class"""
    
    def test_process_current_weather_success(self):
        """Test successful weather data processing"""
        raw_data = {
            'location': {'name': 'Lagos', 'country': 'Nigeria', 'region': 'Lagos'},
            'current': {
                'temp_c': 28.0,
                'condition': {'text': 'Sunny'},
                'humidity': 65
            }
        }
        
        processed = WeatherDataProcessor.process_current_weather(raw_data)
        
        self.assertIsInstance(processed, WeatherData)
        self.assertEqual(processed.location.name, 'Lagos')
    
    def test_validate_weather_data_valid(self):
        """Test weather data validation with valid data"""
        weather_data = WeatherData(
            location=Location('Lagos', 'Nigeria', 'Lagos'),
            current=CurrentWeather(
                temperature_c=28.0, temperature_f=82.4, condition='Sunny',
                icon='', humidity=65, wind_kph=15.0, wind_dir='SW',
                feels_like_c=30.0, uv=7.0, visibility_km=10.0
            )
        )
        
        self.assertTrue(WeatherDataProcessor.validate_weather_data(weather_data))
    
    def test_validate_weather_data_invalid(self):
        """Test weather data validation with invalid data"""
        weather_data = WeatherData(
            location=Location('', '', ''),  # Missing required name
            current=CurrentWeather(
                temperature_c=None, temperature_f=82.4, condition='',
                icon='', humidity=65, wind_kph=15.0, wind_dir='SW',
                feels_like_c=30.0, uv=7.0, visibility_km=10.0
            )
        )
        
        self.assertFalse(WeatherDataProcessor.validate_weather_data(weather_data))


class TestErrorHandling(unittest.TestCase):
    """Test cases for custom exception handling"""
    
    def test_weather_api_error_inheritance(self):
        """Test custom exceptions inherit properly"""
        self.assertTrue(issubclass(NetworkError, WeatherAPIError))
        self.assertTrue(issubclass(CityNotFoundError, WeatherAPIError))
        self.assertTrue(issubclass(APIKeyError, WeatherAPIError))
    
    def test_custom_exception_messages(self):
        """Test custom exception messages"""
        error_msg = "Test error message"
        
        network_error = NetworkError(error_msg)
        city_error = CityNotFoundError(error_msg)
        api_error = APIKeyError(error_msg)
        
        self.assertEqual(str(network_error), error_msg)
        self.assertEqual(str(city_error), error_msg)
        self.assertEqual(str(api_error), error_msg)


if __name__ == '__main__':
    # Configure test output
    unittest.main(verbosity=2)