import requests
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt

def get_week_weather(city_name, api_key, days):
    if days < 1 or days > 7:
        raise ValueError("Количество дней должно быть от 1 до 7.")

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ru',
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            print(f"Ошибка: {data.get('message', 'Неизвестная ошибка')}")
            return []

        # Агрегация данных по дням
        forecast_data = []
        current_date = None
        day_data = None

        for item in data['list']:
            timestamp = datetime.fromtimestamp(item['dt'])
            local_time = timestamp + timedelta(seconds=data['city']['timezone'])
            date = local_time.date()
            hour = local_time.hour

            if current_date != date:
                # Добавляем предыдущий день, если он заполнен
                if day_data and day_data['temp_6am'] is not None and day_data['temp_6pm'] is not None:
                    forecast_data.append(day_data)

                # Начинаем сбор данных для нового дня
                current_date = date
                day_data = {
                    'date': str(date),
                    'temp_6am': None,
                    'temp_6pm': None,
                    'weather_6am': None,
                    'weather_6pm': None,
                    'wind_6am': None,
                    'wind_6pm': None,
                    'clouds_6am': None,
                    'clouds_6pm': None,
                    'id_6am': None,
                    'id_6pm': None,
                    'icon_6am': None,
                    'icon_6pm': None,
                }

            # Заполняем данные для ближайшего времени к 6:00
            if 3 <= hour <= 9:
                if day_data['temp_6am'] is None:
                    day_data['temp_6am'] = item['main']['temp']
                    day_data['weather_6am'] = item['weather'][0]['description']
                    day_data['wind_6am'] = item['wind']['speed']
                    day_data['clouds_6am'] = item['clouds']['all']
                    day_data['id_6am'] = item['weather'][0]['id']
                    day_data['icon_6am'] = item['weather'][0]['icon']

            # Заполняем данные для ближайшего времени к 18:00
            if 15 <= hour <= 21:
                if day_data['temp_6pm'] is None:
                    day_data['temp_6pm'] = item['main']['temp']
                    day_data['weather_6pm'] = item['weather'][0]['description']
                    day_data['wind_6pm'] = item['wind']['speed']
                    day_data['clouds_6pm'] = item['clouds']['all']
                    day_data['id_6pm'] = item['weather'][0]['id']
                    day_data['icon_6pm'] = item['weather'][0]['icon']

        # Добавляем последний день, если он заполнен
        if day_data and day_data['temp_6am'] is not None and day_data['temp_6pm'] is not None:
            forecast_data.append(day_data)

        # Ограничиваем вывод запрашиваемым количеством дней
        return forecast_data[:days]

    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения: {e}")
        return []
    except KeyError as e:
        print(f"Ошибка обработки данных: {e}")
        return []



def get_day_weather(city_name, api_key, cnt):

    farcast_url = ("https://pro.openweathermap.org/data/2.5/forecast")

    farcast_params = {
        'q': city_name,
        'appid': api_key,
        'cnt': cnt,
        'units': 'metric',
        'lang': 'ru',
    }

    try:
        response_farcast = requests.get(farcast_url, params= farcast_params)
        farcast_data = response_farcast.json()



        farcast_correct_data = []

        for i in range(cnt):
            time = datetime.fromtimestamp(farcast_data['list'][i]['dt'], tz = timezone.utc)
            temp_farcast = farcast_data['list'][i]['main']['temp']
            feeling_temp_farcast = farcast_data['list'][i]['main']['feels_like']
            weather_farcast = farcast_data['list'][i]['weather'][0]['description']
            wind = farcast_data['list'][i]['wind']['speed']
            weather_icon = farcast_data['list'][i]['weather'][0]['icon']


            farcast_correct_data.append({
                'time': str(time),
                'temperature': temp_farcast,
                'feels_like': feeling_temp_farcast,
                'weather': weather_farcast,
                'wind': wind,
                'wether_icon_name': weather_icon

            })

        return farcast_correct_data


    except requests.exceptions.RequestException as e:
        print("Ошибка подключения:", e)
    except KeyError:
        print("Ошибка обработки данных. Проверьте название города или API-ключ.")

def temperature_graph(temp_list, feel_temp_list, time):
    x = time
    y1 = temp_list
    y2 = feel_temp_list
    plt.figure(figsize=(10, 4))
    plt.grid(True)


    plt.plot(x, y1, label="Температура", color="blue")
    plt.plot(x, y2, label="Ощущается как", color="red")
    plt.savefig("temperature_graph.png")
    return "temperature_graph.png"


api_key = "4f03e9067c13e35da1032789ecd08df6"
print(get_week_weather('Москва', api_key, 4))



"""test = get_weather('Москва',api_key,8)
print(get_weather('Москва',api_key,9))
temp_list = []
feel_temp_list = []
time = []
for item in test:
    print(item)
    if type(item) == dict:
        time.append(item['time'][11:19])
        temp_list.append(item['temperature'])
        feel_temp_list.append(item['feels_like'])
    else:
        raise TypeError
print(temp_list)
temperature_graph(temp_list, feel_temp_list, time)"""
