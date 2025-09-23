"""
Weather Client Module
Handles API communication with WeatherAPI.com
"""

import requests
import os
from typing import Dict, Any, Optional
from datetime import datetime


class WeatherAPIError(Exception):
    """Base exception for weather API errors"""
    pass


class NetworkError(WeatherAPIError):
    """Network-related errors"""
    pass


class APIKeyError(WeatherAPIError):
    """API key related errors"""
    pass


class CityNotFoundError(WeatherAPIError):
    """City not found errors"""
    pass


class WeatherClient:
    """Client for interacting with WeatherAPI.com"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WeatherClient
        
        Args:
            api_key: WeatherAPI.com API key. If not provided, will try to get from environment
        """
        self.api_key = api_key or os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            raise APIKeyError("WeatherAPI key not found. Please set WEATHER_API_KEY environment variable.")
        
        self.base_url = "http://api.weatherapi.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Weather8/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the WeatherAPI
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            NetworkError: If network request fails
            APIKeyError: If API key is invalid
            WeatherAPIError: For other API errors
        """
        params['key'] = self.api_key
        
        try:
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                raise APIKeyError("Invalid API key")
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Bad request')
                if 'No matching location found' in error_msg:
                    raise CityNotFoundError(error_msg)
                else:
                    raise WeatherAPIError(f"Bad request: {error_msg}")
            elif response.status_code == 403:
                raise APIKeyError("API key quota exceeded or access denied")
            elif response.status_code == 429:
                raise WeatherAPIError("Rate limit exceeded. Please try again later.")
            elif response.status_code != 200:
                raise WeatherAPIError(f"API request failed with status {response.status_code}")
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise NetworkError("Unable to connect to weather service")
        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")
        except ValueError as e:
            raise WeatherAPIError(f"Invalid JSON response: {str(e)}")
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city
        
        Args:
            city: City name (e.g., "London", "New York", "Tokyo")
            
        Returns:
            Current weather data
        """
        params = {
            'q': city,
            'aqi': 'no'  # Don't include air quality data
        }
        
        return self._make_request('current.json', params)
    
    def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """
        Get weather forecast for a city
        
        Args:
            city: City name
            days: Number of forecast days (1-10)
            
        Returns:
            Forecast data
        """
        params = {
            'q': city,
            'days': min(days, 10),  # API limit is 10 days
            'aqi': 'no',
            'alerts': 'no'  # Don't include weather alerts
        }
        
        return self._make_request('forecast.json', params)
    
    def test_connection(self) -> bool:
        """
        Test if the API connection is working
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            # Test with a simple request to London
            self.get_current_weather("London")
            return True
        except Exception:
            return False
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather by coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Current weather data
        """
        params = {
            'q': f"{lat},{lon}",
            'aqi': 'no'
        }
        
        return self._make_request('current.json', params)
    
    def search_cities(self, query: str) -> Dict[str, Any]:
        """
        Search for cities by name
        
        Args:
            query: Search query
            
        Returns:
            List of matching cities
        """
        params = {
            'q': query
        }
        
        return self._make_request('search.json', params)
