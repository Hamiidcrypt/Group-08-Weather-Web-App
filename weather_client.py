"""
Weather8 - WeatherClient Class
Handles all API calls to WeatherAPI.com with error handling and JSON parsing.
"""

import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WeatherAPIError(Exception):
    """Custom exception for Weather API related errors"""
    pass


class NetworkError(WeatherAPIError):
    """Custom exception for network related errors"""
    pass


class APIKeyError(WeatherAPIError):
    """Custom exception for API key related errors"""
    pass


class CityNotFoundError(WeatherAPIError):
    """Custom exception when city is not found"""
    pass


class WeatherClient:
    """
    Encapsulates all API logic and error handling for WeatherAPI.com
    
    Learning objectives covered:
    - API calls (requests)
    - JSON parsing
    - Handling network exceptions
    - Custom exceptions
    """
    
    def __init__(self):
        """Initialize the WeatherClient with API credentials"""
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = os.getenv('WEATHER_API_BASE_URL')
        
        if not self.api_key:
            raise APIKeyError("Weather API key not found in environment variables")
        
        if not self.base_url:
            raise APIKeyError("Weather API base URL not found in environment variables")
        
        # Set up request session with timeout
        self.session = requests.Session()
        self.session.timeout = 10  # 10 second timeout
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """
        Fetch current weather data for a given city
        
        Args:
            city (str): Name of the city to get weather for
            
        Returns:
            Dict[str, Any]: Parsed JSON response with current weather data
            
        Raises:
            NetworkError: For network/connection issues
            CityNotFoundError: When city is not found
            APIKeyError: For API key issues
            WeatherAPIError: For other API errors
        """
        url = f"{self.base_url}/current.json"
        params = {
            'key': self.api_key,
            'q': city,
            'aqi': 'no'  # We don't need air quality data
        }
        
        try:
            response = self.session.get(url, params=params)
            
            # Handle different HTTP status codes
            if response.status_code == 400:
                raise CityNotFoundError(f"City '{city}' not found")
            elif response.status_code == 401:
                raise APIKeyError("Invalid API key")
            elif response.status_code == 403:
                raise APIKeyError("API key limit exceeded")
            elif response.status_code != 200:
                raise WeatherAPIError(f"API returned status code: {response.status_code}")
            
            # Parse JSON response
            try:
                data = response.json()
                return data
            except ValueError as e:
                raise WeatherAPIError(f"Invalid JSON response: {e}")
                
        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Unable to connect to weather service. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error occurred: {e}")
    
    def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """
        Fetch weather forecast data for a given city
        
        Args:
            city (str): Name of the city to get forecast for
            days (int): Number of days to forecast (1-10, default 5)
            
        Returns:
            Dict[str, Any]: Parsed JSON response with forecast data
            
        Raises:
            NetworkError: For network/connection issues
            CityNotFoundError: When city is not found
            APIKeyError: For API key issues
            WeatherAPIError: For other API errors
        """
        # Validate days parameter
        if not 1 <= days <= 10:
            days = 5  # Default to 5 days if invalid
        
        url = f"{self.base_url}/forecast.json"
        params = {
            'key': self.api_key,
            'q': city,
            'days': days,
            'aqi': 'no',
            'alerts': 'no'
        }
        
        try:
            response = self.session.get(url, params=params)
            
            # Handle different HTTP status codes
            if response.status_code == 400:
                raise CityNotFoundError(f"City '{city}' not found")
            elif response.status_code == 401:
                raise APIKeyError("Invalid API key")
            elif response.status_code == 403:
                raise APIKeyError("API key limit exceeded")
            elif response.status_code != 200:
                raise WeatherAPIError(f"API returned status code: {response.status_code}")
            
            # Parse JSON response
            try:
                data = response.json()
                return data
            except ValueError as e:
                raise WeatherAPIError(f"Invalid JSON response: {e}")
                
        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out. Please check your internet connection.")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Unable to connect to weather service. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error occurred: {e}")
    
    def test_connection(self) -> bool:
        """
        Test if the API connection is working
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Test with a simple query
            self.get_current_weather("London")
            return True
        except Exception:
            return False