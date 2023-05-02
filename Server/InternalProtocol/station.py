from .point import Point


class Station():
    def __init__(self, code: int, name: str, location: Point, city: str):
        self.code = code
        self.name = name
        self.city = city
        self.location = location

    def get_id(self):
        return f"{self.city}-{self.code}"

    def get_distance_to(self, other: "Station"):
        return self.location.distance_to(other.location)

    def is_city(self, city_asked):
        return self.city == city_asked
