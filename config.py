import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Чтение токена из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
WEATHER_TOKEN = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL_GEO = 'http://api.openweathermap.org/geo/1.0/direct'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

if not TOKEN or not WEATHER_TOKEN:
    raise NameError