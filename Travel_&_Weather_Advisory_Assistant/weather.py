import requests


def get_coordinates(city: str):

    try:

        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        response = requests.get(
            url,
            params={"name": city},
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results")

        if not results:
            return None

        return (
            results[0]["latitude"],
            results[0]["longitude"]
        )

    except Exception:

        return None


def get_weather(city: str):

    coordinates = get_coordinates(city)

    if not coordinates:

        return {
            "error":
                "Unable to locate destination using geocoding service."
        }

    latitude, longitude = coordinates

    try:

        url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "forecast_days": 7,
            "timezone": "auto"
        }

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        daily = data.get("daily")

        if not daily:

            return {
                "error":
                    "Weather information not available."
            }

        return {
            "destination": city,
            "max_temp":
                daily["temperature_2m_max"][0],

            "min_temp":
                daily["temperature_2m_min"][0],

            "rain_probability":
                daily[
                    "precipitation_probability_max"
                ][0]
        }

    except Exception:

        return {
            "error":
                "Weather service is unavailable."
        }