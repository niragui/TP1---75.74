from typing import Dict
from trip import Trip
from weather import Weather

PRECIPITATION_LIMIT = 30


class RainFilter():
    def __init__(self, trip: Trip, weathers: Dict[str, Weather]):
        super().__init__(trip, weathers, PRECIPITATION_FILTER)

    def run(self):
        city = self.trip.get_city()
        start = self.trip.get_day_start()
        weather_id = f"{city}-{start}"
        weather = self.weathers.get(weather_id)

        if weather is None:
            raise Exception(f"Weather For {city} On {start} Not Found In {self.weathers.keys()}")

        if weather.is_rainy(PRECIPITATION_LIMIT):
            precipitation = weather.get_rain()
            return (self.number, [precipitation])
        else:
            return None
