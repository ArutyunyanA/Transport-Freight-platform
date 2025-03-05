import httpx
from django.conf import settings
from django.db import models
from httpx import HTTPStatusError

async def get_coordinate_async(address):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {
        "access_token": settings.MAPBOX_API_KEY,
        "limit": 1,
        "language": "en"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("features"):
                place = data["features"][0]
                return [
                    place["geometry"]["coordinates"][0],  # Долгота
                    place["geometry"]["coordinates"][1]   # Широта
                ]
        except HTTPStatusError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
    return None


async def get_route(start_coords, end_coords):
    """
    Получение маршрута от Mapbox Directions API.
    Возвращает список маршрутов с расстоянием и временем в пути.
    """
    url = "https://api.mapbox.com/directions/v5/mapbox/driving/{},{};{},{}".format(
        start_coords[0], start_coords[1],
        end_coords[0], end_coords[1]
    )
    params = {
        "alternatives": "true",
        "annotations": "distance,duration",  # Запрашиваем расстояние и время в пути
        "geometries": "geojson",  # Формат геометрии маршрута
        "access_token": settings.MAPBOX_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("routes"):
                routes = data["routes"]
                route_info = []
                for route in routes:
                    distance = route['legs'][0]['distance'] / 1000  # В километрах
                    duration = route['legs'][0]['duration'] / 60  # В минутах
                    route_info.append({
                        "distance": distance,
                        "duration": duration,
                        "geometry": route["geometry"]
                    })
                return route_info
    except HTTPStatusError as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    return None

