from datetime import datetime, date
from station import Station

RAINY_DAY_PRECIPITATION = 30

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class Trip():
    def __init__(self, start_station: str, end_station: str,
                 start_time: datetime, end_time: datetime, city: str):
        self.start = start_station
        self.finish = end_station
        self.begin = start_time
        self.end = end_time
        self.city = city

    def distance(self, stations):
        start = stations.get(self.get_station_start())
        end = stations.get(self.get_station_end())
        return start.get_distance_to(end)

    def time(self):
        return self.end - self.begin

    def get_city(self):
        return self.city

    def get_day_start(self):
        year = self.begin.year
        month = self.begin.month
        day = self.begin.day

        return date(year, month, day)

    def get_day_end(self):
        year = self.end.year
        month = self.end.month
        day = self.end.day

        return date(year, month, day)

    def get_station_end(self):
        return f"{self.city}-{self.finish}"

    def get_station_start(self):
        return f"{self.city}-{self.start}"
