import requests
from config import WEATHER_TOKEN,WEATHER_API_URL_GEO,WEATHER_API_URL

def get_loc(city: str):
    paramsg = {'q':city,'appid':WEATHER_TOKEN}
    urlg = WEATHER_API_URL_GEO
    response_geo = requests.get(urlg, paramsg)
    lat = response_geo.json()[0]['lat']
    lon = response_geo.json()[0]['lon']
    return {'lat':lat, 'lon':lon}

def get_temperature(city: str):
    geo = get_loc(city)
    url = WEATHER_API_URL
    params = {'lat': geo['lat'], 'lon': geo['lon'], 'units': 'metric', 'appid': WEATHER_TOKEN}
    response = requests.get(url, params)
    return response.json()['main']['temp']

def get_food_info(product_name: str):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f"Ошибка: {response.status_code}")
    return None




