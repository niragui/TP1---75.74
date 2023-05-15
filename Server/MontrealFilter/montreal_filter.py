from typing import Dict
from trip import Trip
from station import Station

MONTREAL = "Montreal"


class MontrealFilter():
    def __init__(self, trip: Trip, stations: Dict[str, Station]):
        self.trip = trip
        self.stations = stations

    def run(self):
        city = self.trip.get_city()
        if city != MONTREAL:
            return None

        distance = self.trip.distance(self.stations)
        station = self.trip.get_station_end()
        station_ent = self.stations.get(station)
        name = station_ent.name
        return (station, name, distance)
