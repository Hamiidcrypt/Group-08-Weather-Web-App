"""
Weather8 Domain Models
Wraps API responses in domain classes as required by assignment.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Location:
    """Domain class for location information"""
    name: str
    country: str
    region: str
    local_time: str = ""
    
    @classmethod
    def from_api_response(cls, location_data: Dict[str, Any]) -> 'Location':
        """Create Location object from WeatherAPI response"""
        return cls(
            name=location_data.get('name', 'Unknown'),
            country=location_data.get('country', ''),
            region=location_data.get('region', ''),
            local_time=location_data.get('localtime', '')
        )


@dataclass
class CurrentWeather:
    """Domain class for current weather conditions"""
    temperature_c: float
    temperature_f: float
    condition: str
    icon: str
    humidity: int
    wind_kph: float
    wind_dir: str
    feels_like_c: float
    uv: float
    visibility_km: float
    last_updated: str = ""
    
    @classmethod
    def from_api_response(cls, current_data: Dict[str, Any]) -> 'CurrentWeather':
        """Create CurrentWeather object from WeatherAPI response"""
        return cls(
            temperature_c=current_data.get('temp_c', 0.0),
            temperature_f=current_data.get('temp_f', 0.0),
            condition=current_data.get('condition', {}).get('text', 'Unknown'),
            icon=current_data.get('condition', {}).get('icon', ''),
            humidity=current_data.get('humidity', 0),
            wind_kph=current_data.get('wind_kph', 0.0),
            wind_dir=current_data.get('wind_dir', ''),
            feels_like_c=current_data.get('feelslike_c', 0.0),
            uv=current_data.get('uv', 0.0),
            visibility_km=current_data.get('vis_km', 0.0),
            last_updated=current_data.get('last_updated', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'temperature_c': self.temperature_c,
            'temperature_f': self.temperature_f,
            'condition': self.condition,
            'icon': self.icon,
            'humidity': self.humidity,
            'wind_kph': self.wind_kph,
            'wind_dir': self.wind_dir,
            'feels_like_c': self.feels_like_c,
            'uv': self.uv,
            'visibility_km': self.visibility_km
        }


@dataclass
class ForecastDay:
    """Domain class for a single forecast day"""
    date: str
    max_temp_c: float
    min_temp_c: float
    max_temp_f: float
    min_temp_f: float
    condition: str
    icon: str
    chance_of_rain: int
    avg_humidity: int
    
    @classmethod
    def from_api_response(cls, day_data: Dict[str, Any]) -> 'ForecastDay':
        """Create ForecastDay object from WeatherAPI response"""
        day = day_data.get('day', {})
        return cls(
            date=day_data.get('date', ''),
            max_temp_c=day.get('maxtemp_c', 0.0),
            min_temp_c=day.get('mintemp_c', 0.0),
            max_temp_f=day.get('maxtemp_f', 0.0),
            min_temp_f=day.get('mintemp_f', 0.0),
            condition=day.get('condition', {}).get('text', 'Unknown'),
            icon=day.get('condition', {}).get('icon', ''),
            chance_of_rain=day.get('daily_chance_of_rain', 0),
            avg_humidity=day.get('avghumidity', 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'date': self.date,
            'max_temp_c': self.max_temp_c,
            'min_temp_c': self.min_temp_c,
            'max_temp_f': self.max_temp_f,
            'min_temp_f': self.min_temp_f,
            'condition': self.condition,
            'icon': self.icon,
            'chance_of_rain': self.chance_of_rain,
            'avg_humidity': self.avg_humidity
        }


@dataclass
class WeatherData:
    """Complete weather data domain class"""
    location: Location
    current: CurrentWeather
    last_updated: str = ""
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> 'WeatherData':
        """Create WeatherData object from WeatherAPI response"""
        return cls(
            location=Location.from_api_response(api_data.get('location', {})),
            current=CurrentWeather.from_api_response(api_data.get('current', {})),
            last_updated=api_data.get('current', {}).get('last_updated', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'location': {
                'name': self.location.name,
                'country': self.location.country,
                'region': self.location.region,
                'local_time': self.location.local_time
            },
            'current': self.current.to_dict(),
            'last_updated': self.last_updated
        }


@dataclass
class WeatherForecast:
    """Complete forecast data domain class"""
    location: Location
    forecast: List[ForecastDay]
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any]) -> 'WeatherForecast':
        """Create WeatherForecast object from WeatherAPI response"""
        forecast_days = []
        for day_data in api_data.get('forecast', {}).get('forecastday', []):
            forecast_days.append(ForecastDay.from_api_response(day_data))
        
        return cls(
            location=Location.from_api_response(api_data.get('location', {})),
            forecast=forecast_days
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'location': {
                'name': self.location.name,
                'country': self.location.country,
                'region': self.location.region
            },
            'forecast': [day.to_dict() for day in self.forecast]
        }


class WeatherDataProcessor:
    """
    Utility class to process raw API responses into domain objects
    Demonstrates proper separation of concerns
    """
    
    @staticmethod
    def process_current_weather(raw_api_data: Dict[str, Any]) -> WeatherData:
        """
        Process raw API data into structured WeatherData object
        
        Args:
            raw_api_data: Raw JSON response from WeatherAPI
            
        Returns:
            WeatherData: Structured domain object
        """
        try:
            return WeatherData.from_api_response(raw_api_data)
        except Exception as e:
            raise ValueError(f"Failed to process weather data: {e}")
    
    @staticmethod
    def process_forecast(raw_api_data: Dict[str, Any]) -> WeatherForecast:
        """
        Process raw API forecast data into structured WeatherForecast object
        
        Args:
            raw_api_data: Raw JSON response from WeatherAPI
            
        Returns:
            WeatherForecast: Structured domain object
        """
        try:
            return WeatherForecast.from_api_response(raw_api_data)
        except Exception as e:
            raise ValueError(f"Failed to process forecast data: {e}")
    
    @staticmethod
    def validate_weather_data(weather_data: WeatherData) -> bool:
        """
        Validate that weather data contains required fields
        
        Args:
            weather_data: WeatherData object to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check required fields exist
            return (
                weather_data.location.name and
                weather_data.current.temperature_c is not None and
                weather_data.current.condition
            )
        except (AttributeError, TypeError):
            return False
    
    @staticmethod
    def validate_forecast_data(forecast_data: WeatherForecast) -> bool:
        """
        Validate that forecast data contains required fields
        
        Args:
            forecast_data: WeatherForecast object to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            return (
                forecast_data.location.name and
                len(forecast_data.forecast) > 0 and
                all(day.date for day in forecast_data.forecast)
            )
        except (AttributeError, TypeError):
            return False