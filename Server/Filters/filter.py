from typing import Dict
from ..InternalProtocol.trip import Trip
from ..InternalProtocol.weather import Weather


class Filter():
    def __init__(self, trip: Trip, weathers: Dict[str, Weather], filter_id: int):
        self.trip = trip
        self.weathers = weathers
        self.number = filter_id

    def run(self):
        """
        Runs the filtering and return None if not useful
        or the values to send the Joiner if useful

        To Be Implemented in Subclass
        """
        return None