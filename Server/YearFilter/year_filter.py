from typing import Dict
from trip import Trip
from station import Station

SEARCHED_YEARS = [2016, 2017]

NEGATIVE_VALUE = -2
POSITIVE_VALUE = 1


class YearFilter():
    def __init__(self, trip: Trip, stations: Dict[str, Station]):
        self.trip = trip
        self.stations = stations

    def run(self):
        date = self.trip.get_day_start()
        year = date.year

        if year not in SEARCHED_YEARS:
            return None

        station = self.trip.get_station_end()
        station_ent = self.stations.get(station)
        if station_ent is None:
            return None
        name = station_ent.name
        if year == 2016:
            return (name, NEGATIVE_VALUE)
        else:
            return (name, POSITIVE_VALUE)
