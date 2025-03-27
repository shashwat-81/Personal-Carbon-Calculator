import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import streamlit as st

# Load environment variables
load_dotenv()

class LocationServices:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="carbon_calculator")
        self.api_key = os.getenv('OPENAQ_API_KEY', '')  # OpenAQ API key
        
    def get_location_from_coordinates(self, latitude, longitude):
        """Get location details from coordinates"""
        try:
            location = self.geolocator.reverse((latitude, longitude), language='en')
            if location:
                return location.address
            return None
        except GeocoderTimedOut:
            return None
            
    def get_air_quality_data(self, latitude, longitude):
        """Get real-time air quality data"""
        try:
            # OpenAQ API endpoint for latest measurements
            url = f"https://api.openaq.org/v2/latest?coordinates={latitude},{longitude}&radius=10000&limit=1"
            headers = {
                'X-Api-Key': self.api_key,
                'Accept': 'application/json'
            }
            
            print(f"Fetching air quality data for coordinates: {latitude}, {longitude}")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"API Response: {data}")
                
                if data.get('results'):
                    result = data['results'][0]
                    measurements = result.get('measurements', [])
                    
                    # Extract measurements
                    pm25 = next((m['value'] for m in measurements if m['parameter'] == 'pm25'), None)
                    pm10 = next((m['value'] for m in measurements if m['parameter'] == 'pm10'), None)
                    
                    print(f"Found measurements - PM2.5: {pm25}, PM10: {pm10}")
                    
                    # Calculate AQI based on PM2.5 (US EPA standard)
                    aqi = self.calculate_aqi(pm25) if pm25 else None
                    
                    return {
                        'aqi': aqi,
                        'pm25': pm25,
                        'pm10': pm10,
                        'temperature': 25,  # OpenAQ doesn't provide temperature
                        'humidity': 50,     # OpenAQ doesn't provide humidity
                        'wind_speed': 5     # OpenAQ doesn't provide wind speed
                    }
                else:
                    print("No results found in API response")
            else:
                print(f"API request failed with status code: {response.status_code}")
                print(f"Response content: {response.text}")
            return None
        except Exception as e:
            print(f"Error fetching air quality data: {str(e)}")
            return None
            
    def calculate_aqi(self, pm25):
        """Calculate AQI based on PM2.5 concentration using US EPA standard"""
        if not pm25:
            return None
            
        # AQI breakpoints for PM2.5
        breakpoints = [
            (0, 12.0, 0, 50),      # Good
            (12.1, 35.4, 51, 100), # Moderate
            (35.5, 55.4, 101, 150),# Unhealthy for Sensitive Groups
            (55.5, 150.4, 151, 200),# Unhealthy
            (150.5, 250.4, 201, 300),# Very Unhealthy
            (250.5, 500.4, 301, 500) # Hazardous
        ]
        
        for low, high, aqi_low, aqi_high in breakpoints:
            if low <= pm25 <= high:
                return round(((aqi_high - aqi_low) / (high - low)) * (pm25 - low) + aqi_low)
        
        return 500  # If PM2.5 is above 500.4

    def calculate_health_impact(self, aqi):
        """Calculate health impact based on AQI"""
        if not aqi:
            return "Unknown", "No data available"
            
        if aqi <= 50:
            return "Good", "Air quality is satisfactory, and air pollution poses little or no risk."
        elif aqi <= 100:
            return "Moderate", "Air quality is acceptable. However, there may be a risk for some people."
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups", "Some members of the general public may experience health effects."
        elif aqi <= 200:
            return "Unhealthy", "Some members of the general public may experience health effects."
        elif aqi <= 300:
            return "Very Unhealthy", "Health alert: The risk of health effects is increased for everyone."
        else:
            return "Hazardous", "Health warning of emergency conditions: everyone is more likely to be affected."

    def get_historical_data(self, latitude, longitude):
        """Get historical air quality data"""
        try:
            # OpenAQ API endpoint for historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            url = f"https://api.openaq.org/v2/measurements?coordinates={latitude},{longitude}&radius=10000&date_from={start_date.isoformat()}&date_to={end_date.isoformat()}&limit=100"
            headers = {
                'X-Api-Key': self.api_key,
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    return [{
                        'timestamp': result['date']['utc'],
                        'aqi': self.calculate_aqi(result['value']) if result['parameter'] == 'pm25' else None
                    } for result in data['results'] if result['parameter'] == 'pm25']
            return None
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return None 