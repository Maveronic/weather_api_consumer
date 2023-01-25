from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
import requests
from decouple import config
from rest_framework import status


# Create your views here.
@api_view(['POST'])
def weather(request):
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    API_KEY = config('WEATHER_API_KEY')
    CITY = request.data.get('city')

    if 'city' not in request.data:
        return Response({'error': 'city key not found in payload'}, status=status.HTTP_400_BAD_REQUEST)
    if request.data.get('city') == "":
        return Response({'error': 'Invalid city name'}, status=status.HTTP_400_BAD_REQUEST)

    def kelvin_to_celsius_fahrenheit(kelvin):
        celsius = kelvin - 273.15
        fahrenheit = celsius * (9 / 5) + 32
        return celsius, fahrenheit

    url = BASE_URL + "appid=" + str(API_KEY) + "&q=" + CITY

    try:
        response = requests.get(url).json()

        temp_kelvin = response['main']['temp']
        temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)

        feels_like_kelvin = response['main']['feels_like']
        feels_like_celsius, feels_like_fahrenheit = kelvin_to_celsius_fahrenheit(feels_like_kelvin)
        humidity = response['main']['humidity']
        wind_speed = response['wind']['speed']
        description = response['weather'][0]['description']
        sunrise_time = datetime.datetime.utcfromtimestamp(response['sys']['sunrise'] + response['timezone'])
        sunset_time = datetime.datetime.utcfromtimestamp(response['sys']['sunset'] + response['timezone'])

        data = {
            'temperature': {
                'celsius': temp_celsius,
                'fahrenheit': temp_fahrenheit
            },
            'feels_like': {
                'celsius': feels_like_celsius,
                'fahrenheit': feels_like_fahrenheit
            },
            'humidity': humidity,
            'wind_speed': wind_speed,
            'description': description,
            'sunrise_time': sunrise_time,
            'sunset_time': sunset_time
        }
        return Response(data)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except KeyError as e:
        return Response({'error': 'Invalid city name'}, status=status.HTTP_400_BAD_REQUEST)


