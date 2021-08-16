import os
import json
import requests

from dotenv import load_dotenv
from geopy import distance
import folium
from flask import Flask


def get_input_coordinates(address, api_key):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    params = {
        'geocode': address,
        'apikey': api_key,
        'format': 'json'
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_coffee_points(file):
    with open(file, 'r', encoding='CP1251') as file:
        file_content = file.read()
    coffee_json = json.loads(file_content)
    coffee_points = []

    for point in coffee_json:
        lat, lon = point['geoData']['coordinates']
        name = point['Name']

        point = {
            'title': name,
            'latitude': lat,
            'longitude': lon
        }
        coffee_points.append(point)
    return coffee_points


def get_nearest_points(point):
    return point['distance']


def get_distance(my_place_coords, coffee_shops_coords):
    distance_to_shop = distance.distance(
        my_place_coords,
        coffee_shops_coords
    ).km
    return distance_to_shop


def generate_map(coords, points):
    map = folium.Map(location=coords, zoom_start=13, tiles='cartodb positron')
    for point in points:
        folium.Marker(
            location=[point['longitude'], point['latitude']],
            popup=point['title'],
            icon=folium.Icon(color ='blue')
        ).add_to(map)
    map.save("map.html")


def get_map():
    with open('map.html') as file:
        return file.read()


def create_app():
    app = Flask(__name__)
    app.add_url_rule('/', 'map', get_map)
    app.run('0.0.0.0', debug=True)


def main():
    load_dotenv()

    file = 'coffee.json'
    ya_key = os.getenv('YA_API_KEY')
    input_address = input('Где Вы находитесь: ')
    coords = get_input_coordinates(input_address, ya_key)
    coffee_points = get_coffee_points(file)

    for point in coffee_points:
        distance = get_distance(
            coords,
            (
                point['longitude'], 
                point['latitude']
            )
        )
        point['distance'] = distance

    top_5_nearest_points = sorted(coffee_points, key=get_nearest_points)[:5]
    generate_map(coords, top_5_nearest_points)
    create_app()
    

if __name__ == '__main__':
    main()
