from datetime import datetime, date
from station import Station

RAINY_DAY_PRECIPITATION = 30


class Trip():
    def __init__(self, start_station: Station, end_station: Station,
                 start_time: datetime, end_time: datetime, city: str):
        self.start = start_station
        self.finish = end_station
        self.begin = start_time
        self.end = end_time
        self.city = city

    def distance(self):
        return self.start.get_distance_to(self.finish)

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
        return self.finish.get_id()

    def get_station_start(self):
        return self.start.get_id()