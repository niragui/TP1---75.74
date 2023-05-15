from haversine import haversine


class Point():
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def get_position(self):
        return (self.latitude, self.longitude)

    def distance_to(self, other: "Point"):
        start = self.get_position()
        end = other.get_position()

        return haversine(start, end)
