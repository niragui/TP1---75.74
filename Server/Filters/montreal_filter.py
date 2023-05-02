from .filter import Filter
from typing import Dict
from ..InternalProtocol.trip import Trip
from ..InternalProtocol.weather import Weather
from ..InternalProtocol.joinerprotocol import MONTREAL_FILTER

PRECIPITATION_LIMIT = 30
MONTREAL = "Montreal"


class MontrealFilter(Filter):
    def __init__(self, trip: Trip, weathers: Dict[str, Weather]):
        super().__init__(trip, weathers, MONTREAL_FILTER)

    def run(self):
        city = self.trip.get_city()
        if city != MONTREAL:
            return None

        distance = self.trip.distance()
        station = self.trip.get_station_end()
        return (self.number, [station, distance])
