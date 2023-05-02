from .filter import Filter
from typing import Dict
from ..InternalProtocol.trip import Trip
from ..InternalProtocol.weather import Weather
from ..InternalProtocol.joinerprotocol import PRECIPITATION_FILTER

PRECIPITATION_LIMIT = 30


class PrecipitationFilter(Filter):
    def __init__(self, trip: Trip, weathers: Dict[str, Weather]):
        super().__init__(trip, weathers, PRECIPITATION_FILTER)

    def run(self):
        city = self.trip.get_city()
        start = self.trip.get_day_start()
        weather_id = f"{city}-{start}"
        weather = self.weathers.get(weather_id)

        if weather is None:
            raise Exception(f"Weather For {city} On {start} Not Found")

        if weather.is_rainy(PRECIPITATION_LIMIT):
            precipitation = weather.get_rain()
            return (self.number, [precipitation])
        else:
            return None
