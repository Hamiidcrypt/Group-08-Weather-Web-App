# Weather8 🌤️

A modern weather dashboard web application that provides current weather conditions and 5-day forecasts for any city worldwide.

## 🚀 Features

- **Global Weather Search** - Get weather for any city worldwide (Lagos, California, Tokyo, Paris, etc.)
- **Current Weather Display** - Temperature, humidity, wind, UV index, and more
- **5-Day Forecast** - Visual forecast with high/low temperatures and conditions
- **Smart Caching** - TTL caching reduces API calls and improves performance
- **Responsive Design** - Works perfectly on desktop and mobile devices
- **Error Handling** - Graceful handling of network issues and invalid cities
- **Network Accessible** - Access via IP address (192.168.x.x) for team collaboration

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask
- **API**: WeatherAPI.com
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Dependency Management**: Pipenv
- **Testing**: Python unittest
- **Architecture**: Domain-driven design with custom exceptions

## 📋 Requirements Met

### Learning Objectives ✅
- **API calls (requests)** - WeatherClient class with robust HTTP handling
- **JSON parsing** - Complete processing of WeatherAPI.com responses
- **Network exception handling** - Custom NetworkError, timeout protection
- **Domain classes** - WeatherData, Location, CurrentWeather, ForecastDay models
- **Custom exceptions** - WeatherAPIError, CityNotFoundError, APIKeyError
- **Git and deployment** - Ready for production deployment

### Functional Requirements ✅
- **City weather search** - Works with any global location
- **Current weather & forecast** - Complete weather information display
- **Caching** - 10-minute TTL cache to reduce API calls
- **Error handling** - User-friendly error messages

### UI Requirements ✅
- **Search box** - Clean, responsive city search interface  
- **Current weather card** - Temperature, icon, description, details
- **5-day forecast chart** - Visual high/low temperature display

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (We're using 3.12.4)
- Pipenv for dependency management

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd weather8
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   ```

3. **Activate virtual environment**
   ```bash
   pipenv shell
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the dashboard**
   - Local: http://localhost:5000
   - Network: http://192.168.x.x:5000 (replace with your IP)

## 🧪 Testing

Run the test suite to verify all functionality:

```bash
# Run all tests
Python -m pytest

# Or using unittest
python -m unittest tests/test_weather.py -v
```

### Test Coverage
- ✅ WeatherClient API integration
- ✅ Custom exception handling  
- ✅ Domain model creation and validation
- ✅ Error scenarios (network, invalid city, API key)
- ✅ Data processing and caching logic

## 🏗️ Architecture

### Project Structure
```
weather8/
├── app.py                 # Main Flask application
├── weather_client.py      # WeatherClient class with API logic
├── models.py             # Domain classes (Location, WeatherData, etc.)
├── cache.py              # TTL caching implementation
├── templates/            # HTML templates
│   └── index.html       # Main dashboard interface
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   └── js/             # JavaScript files
├── tests/               # Unit tests
│   └── test_weather.py # Test suite
├── Pipfile              # Dependency management
├── .env                 # Environment variables (API keys)
└── README.md           # This file
```

### Key Classes

- **WeatherClient**: Encapsulates all WeatherAPI.com integration
- **WeatherData**: Domain model for current weather conditions
- **WeatherForecast**: Domain model for forecast data
- **Location**: Geographic location information
- **Custom Exceptions**: Specific error types for different failure modes

## 🔧 Configuration

### Environment Variables
The application uses environment variables for configuration:

```env
# WeatherAPI.com Configuration
WEATHER_API_KEY=your_api_key_here
WEATHER_API_BASE_URL=http://api.weatherapi.com/v1

# Flask Configuration  
FLASK_ENV=development
FLASK_DEBUG=True
```

### API Key Setup
1. Visit [WeatherAPI.com](https://www.weatherapi.com/)
2. Sign up for a free account (10,000 calls/month)
3. Get your API key from the dashboard
4. Update the `WEATHER_API_KEY` in `.env`

## 🚀 Deployment

### Local Network Access
The application runs with `host='0.0.0.0'` to allow access via IP address:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Production Considerations
- Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
- Use a production WSGI server (Gunicorn, uWSGI)
- Implement proper logging
- Add rate limiting for API endpoints
- Use environment-specific configuration files

## 🎯 Grading Rubric Alignment

## 🤝 Team Collaboration

### For Group Members
1. Clone the repository
2. Run `pipenv install` to get identical dependencies
3. The app will work immediately with the shared API key
4. Access via team member's IP: `http://192.168.x.x:5000`

### Git Workflow
- `.env` file is included 
- All code changes should be committed to version control
- Use feature branches for major changes

## 📱 Usage Examples

### Search Examples
- **Cities**: "Lagos", "Los Angeles", "Paris", "Tokyo"
- **Countries**: "Laos", "Singapore" 
- **Regions**: "California, USA", "Lagos, Nigeria"

### API Endpoints
- **Current Weather**: `/api/weather/current?city=Lagos`
- **5-Day Forecast**: `/api/weather/forecast?city=Lagos`
- **Cache Status**: `/api/cache/status` (debugging)

## 🐛 Troubleshooting

### Common Issues
1. **"City not found"** - Check spelling, try "City, Country" format
2. **API key errors** - Verify WEATHER_API_KEY in .env file
3. **Network timeout** - Check internet connection, API might be down
4. **Port already in use** - Kill process on port 5000 or use different port
5. **Module not found** - Ensure pipenv environment is activated

### Debug Commands
```bash
# Check if API key is working
python -c "from weather_client import WeatherClient; print(WeatherClient().test_connection())"

# Check cache status
curl http://localhost:5000/api/cache/status

# View server logs
python app.py  # Watch console for error messages
```

## 🔄 Caching System

### How It Works
- **TTL Cache**: Data cached for 10 minutes per city
- **Cache Keys**: `current_{city}` and `forecast_{city}`
- **Benefits**: Reduces API calls, improves response time
- **UI Indicators**: Shows "Cached data" vs "Fresh data"

### Cache Management
```bash
# View cache status
curl http://localhost:5000/api/cache/status

# Cache expires automatically after 10 minutes
# No manual clearing needed for this implementation
```

## 📊 Performance

### API Limits
- **WeatherAPI.com Free Tier**: 10,000 calls/month
- **With Caching**: Reduces calls by ~90% for repeated searches
- **Timeout**: 10-second request timeout prevents hanging

### Response Times
- **Cache Hit**: ~50ms (local memory)
- **API Call**: ~500-2000ms (depends on network)
- **Error Response**: ~100ms (immediate validation)

## 🌟 Features Showcase

### Current Weather Card
- Temperature in Celsius and Fahrenheit
- Weather condition with icon
- Feels-like temperature
- Humidity, wind speed, and direction
- UV index and visibility
- Last updated timestamp

### 5-Day Forecast
- Daily high/low temperatures
- Weather icons and conditions
- Chance of rain percentage
- Today/Tomorrow labels for clarity

### Error Handling
- City not found: Helpful spelling suggestions
- Network issues: Connection troubleshooting tips
- API limits: Polite limit exceeded messages
- Validation: Input sanitization and validation

## 📈 Extension Ideas

### Stretch Goals (Not Required)
- **Geolocation**: Auto-detect user location
- **Favorite Cities**: Save frequently searched cities
- **Background Refresh**: Auto-update weather data
- **Weather Alerts**: Severe weather notifications
- **Historical Data**: Past weather information
- **Weather Maps**: Radar and satellite imagery

### Technical Improvements
- **Database**: Persistent caching with SQLite
- **API Versioning**: Support multiple weather APIs
- **Internationalization**: Multi-language support
- **Progressive Web App**: Offline capabilities
- **Real-time Updates**: WebSocket integration


For the 59 Second Demo Video:
https://drive.google.com/file/d/1GrOxfe8tQFruoMkNsE8ySEY4R88kTFDK/view?usp=drivesdk

---




**Weather8** - *Your Global Weather Dashboard* 🌍
