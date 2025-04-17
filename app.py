# Import required libraries
from flask import Flask, request, jsonify
import requests
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Replace with your OpenWeatherMap API key
API_KEY = 'e7338b007df85f7b48c56a9ece3bf371'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('weather.db')
    conn.execute('CREATE TABLE IF NOT EXISTS cache (city TEXT PRIMARY KEY, weather TEXT)')
    conn.close()

# GET: Fetch weather for a city
@app.route('/weather', methods=['GET'])
def get_weather():
    # Get city from query parameter
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City is required'}), 400

     # Check cache
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute('SELECT weather FROM cache WHERE city = ?', (city,))
    cached = cursor.fetchone()
    if cached:
        conn.close()
        return jsonify({'source': 'cache', 'weather': cached[0]})

    # Fetch from OpenWeatherMap
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        temp = weather_data['main']['temp']
        desc = weather_data['weather'][0]['description']
        result = f'{temp}°C, {desc}'
        # Cache the result
        cursor.execute('INSERT OR REPLACE INTO cache (city, weather) VALUES (?, ?)', (city, result))
        conn.commit()
        conn.close()
        return jsonify({'source': 'api', 'weather': result})
    return jsonify({'error': 'City not found'}), 404

# Run the app
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)