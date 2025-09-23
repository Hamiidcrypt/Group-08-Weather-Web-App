"""
Weather8 - Main Flask Application
A web dashboard for weather data with current conditions and 5-day forecast.
"""

from flask import Flask, render_template, request, jsonify, flash
import os
from dotenv import load_dotenv
from weather_client import WeatherClient, WeatherAPIError, NetworkError, CityNotFoundError, APIKeyError
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'weather8-dev-key-change-in-production')

# Initialize WeatherClient
try:
    weather_client = WeatherClient()
    print("✅ WeatherClient initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize WeatherClient: {e}")
    weather_client = None

# Simple in-memory cache for API results (TTL caching)
cache = {}
CACHE_DURATION = timedelta(minutes=10)  # Cache for 10 minutes


def is_cache_valid(timestamp):
    """Check if cached data is still valid (within TTL)"""
    return datetime.now() - timestamp < CACHE_DURATION


def get_cached_data(cache_key):
    """Get data from cache if valid, None otherwise"""
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if is_cache_valid(timestamp):
            return data
    return None


def set_cache_data(cache_key, data):
    """Store data in cache with current timestamp"""
    cache[cache_key] = (data, datetime.now())


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/weather/current')
def get_current_weather():
    """
    API endpoint for current weather data
    Query parameter: city
    """
    city = request.args.get('city', '').strip()
    
    if not city:
        return jsonify({
            'success': False,
            'error': 'City parameter is required'
        }), 400
    
    if not weather_client:
        return jsonify({
            'success': False,
            'error': 'Weather service is not available'
        }), 500
    
    # Check cache first
    cache_key = f"current_{city.lower()}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return jsonify({
            'success': True,
            'data': cached_data,
            'cached': True
        })
    
    try:
        # Fetch current weather data
        weather_data = weather_client.get_current_weather(city)
        
        # Extract relevant information
        current = weather_data.get('current', {})
        location = weather_data.get('location', {})
        
        result = {
            'location': {
                'name': location.get('name', 'Unknown'),
                'country': location.get('country', ''),
                'region': location.get('region', ''),
                'local_time': location.get('localtime', '')
            },
            'current': {
                'temperature_c': current.get('temp_c', 0),
                'temperature_f': current.get('temp_f', 0),
                'condition': current.get('condition', {}).get('text', 'Unknown'),
                'icon': current.get('condition', {}).get('icon', ''),
                'humidity': current.get('humidity', 0),
                'wind_kph': current.get('wind_kph', 0),
                'wind_dir': current.get('wind_dir', ''),
                'feels_like_c': current.get('feelslike_c', 0),
                'uv': current.get('uv', 0),
                'visibility_km': current.get('vis_km', 0)
            },
            'last_updated': current.get('last_updated', '')
        }
        
        # Cache the result
        set_cache_data(cache_key, result)
        
        return jsonify({
            'success': True,
            'data': result,
            'cached': False
        })
        
    except CityNotFoundError:
        return jsonify({
            'success': False,
            'error': f"City '{city}' not found. Please check the spelling and try again."
        }), 404
        
    except APIKeyError as e:
        return jsonify({
            'success': False,
            'error': 'Weather service authentication error. Please try again later.'
        }), 401
        
    except NetworkError as e:
        return jsonify({
            'success': False,
            'error': 'Unable to connect to weather service. Please check your internet connection.'
        }), 503
        
    except WeatherAPIError as e:
        return jsonify({
            'success': False,
            'error': f'Weather service error: {str(e)}'
        }), 500
        
    except Exception as e:
        print(f"Unexpected error in get_current_weather: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@app.route('/api/weather/forecast')
def get_forecast():
    """
    API endpoint for 5-day weather forecast
    Query parameter: city
    """
    city = request.args.get('city', '').strip()
    
    if not city:
        return jsonify({
            'success': False,
            'error': 'City parameter is required'
        }), 400
    
    if not weather_client:
        return jsonify({
            'success': False,
            'error': 'Weather service is not available'
        }), 500
    
    # Check cache first
    cache_key = f"forecast_{city.lower()}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        return jsonify({
            'success': True,
            'data': cached_data,
            'cached': True
        })
    
    try:
        # Fetch 5-day forecast data
        forecast_data = weather_client.get_forecast(city, days=5)
        
        # Extract relevant information
        location = forecast_data.get('location', {})
        forecast_days = forecast_data.get('forecast', {}).get('forecastday', [])
        
        result = {
            'location': {
                'name': location.get('name', 'Unknown'),
                'country': location.get('country', ''),
                'region': location.get('region', '')
            },
            'forecast': []
        }
        
        # Process each forecast day
        for day_data in forecast_days:
            day = day_data.get('day', {})
            result['forecast'].append({
                'date': day_data.get('date', ''),
                'max_temp_c': day.get('maxtemp_c', 0),
                'min_temp_c': day.get('mintemp_c', 0),
                'max_temp_f': day.get('maxtemp_f', 0),
                'min_temp_f': day.get('mintemp_f', 0),
                'condition': day.get('condition', {}).get('text', 'Unknown'),
                'icon': day.get('condition', {}).get('icon', ''),
                'chance_of_rain': day.get('daily_chance_of_rain', 0),
                'avg_humidity': day.get('avghumidity', 0)
            })
        
        # Cache the result
        set_cache_data(cache_key, result)
        
        return jsonify({
            'success': True,
            'data': result,
            'cached': False
        })
        
    except CityNotFoundError:
        return jsonify({
            'success': False,
            'error': f"City '{city}' not found. Please check the spelling and try again."
        }), 404
        
    except APIKeyError as e:
        return jsonify({
            'success': False,
            'error': 'Weather service authentication error. Please try again later.'
        }), 401
        
    except NetworkError as e:
        return jsonify({
            'success': False,
            'error': 'Unable to connect to weather service. Please check your internet connection.'
        }), 503
        
    except WeatherAPIError as e:
        return jsonify({
            'success': False,
            'error': f'Weather service error: {str(e)}'
        }), 500
        
    except Exception as e:
        print(f"Unexpected error in get_forecast: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@app.route('/api/cache/status')
def cache_status():
    """Debug endpoint to check cache status"""
    cache_info = {}
    for key, (data, timestamp) in cache.items():
        cache_info[key] = {
            'timestamp': timestamp.isoformat(),
            'valid': is_cache_valid(timestamp),
            'age_minutes': (datetime.now() - timestamp).total_seconds() / 60
        }
    
    return jsonify({
        'cache_entries': len(cache),
        'cache_details': cache_info,
        'cache_duration_minutes': CACHE_DURATION.total_seconds() / 60
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Check if WeatherClient is working
    if weather_client and weather_client.test_connection():
        print("🌤️  Weather8 is ready!")
        print("🔗 WeatherAPI connection: ✅ Working")
    else:
        print("⚠️  Warning: WeatherAPI connection issues detected")
    
    # Run Flask app
    # host='0.0.0.0' makes it accessible via IP address (192.168.x.x)
    app.run(
        host='0.0.0.0',  # Accessible from network
        port=5000,
        debug=True
    )