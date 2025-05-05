# Freeriding Snow Forecast Assistant

This is a Dash-based prototype app designed to help freeride skiers evaluate snow conditions across ski resorts in the Pyrenees. The app provides a classification system based on snowfall, temperature, and wind, and includes an AI assistant that gives natural language recommendations for where to ski.

## File Descriptions

- `app.py`: Main Dash application with the layout, callbacks, and interactive map.
- `assistant.py`: Handles text generation using Cohere (single and multi-resort reports).
- `api_utils.py`: Fetches hourly weather data from Open-Meteo API.
- `resorts.py`: Contains coordinates of all ski resorts used in the app.
- `.env`: Stores your Cohere API key (not tracked by Git).
- `requirements.txt`: Lists required Python libraries and versions.

## Python Version

- Python 3.11

## Libraries Used

- dash
- dash-leaflet
- pandas
- plotly
- numpy
- requests
- cohere
- python-dotenv

## Setup

1. Install dependencies:

pip install -r requirements.txt

2. Add your Cohere API key to a `.env` file:

COHERE_API_KEY=your_key_here

3. Run the app:

python app.py