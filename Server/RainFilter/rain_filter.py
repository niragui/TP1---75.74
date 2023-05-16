from typing import Dict
from trip import Trip
from weather import Weather

PRECIPITATION_LIMIT = 30


class RainFilter():
    def __init__(self, trip: Trip, weathers: Dict[str, Weather]):
        self.trip = trip
        self.weathers = weathers

    def run(self):
        city = self.trip.get_city()
        start = self.trip.get_day_start()
        weather_id = f"{city}-{start}"
        weather = self.weathers.get(weather_id)

        if weather is None:
            return None

        if weather.is_rainy(PRECIPITATION_LIMIT):
            duration = self.trip.get_duration()
            return (start.isoformat(), duration)
        else:
            return None
