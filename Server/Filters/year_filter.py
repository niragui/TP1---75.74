from .filter import Filter
from typing import Dict
from ..InternalProtocol.trip import Trip
from ..InternalProtocol.weather import Weather
from ..InternalProtocol.joinerprotocol import YEAR_FILTER

PRECIPITATION_LIMIT = 30
MONTREAL = "Montreal"

SEARCHED_YEARS = [2016, 2017]


class YearFilter(Filter):
    def __init__(self, trip: Trip, weathers: Dict[str, Weather]):
        super().__init__(trip, weathers, YEAR_FILTER)

    def run(self):
        date = self.trip.get_day_start()
        year = date.year
        if year not in SEARCHED_YEARS:
            return None

        station = self.trip.get_station_end()
        if year == 2016:
            return (self.number, [station, -2])
        else:
            return (self.number, [station, 1])
