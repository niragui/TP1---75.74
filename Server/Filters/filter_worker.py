from .prec_filter import PrecipitationFilter
from .year_filter import YearFilter
from .montreal_filter import MontrealFilter

from ..InternalProtocol.serverfilterprotocol import read_message
from ..InternalProtocol.constants import STOP_TYPE
from ..InternalProtocol.trip import Trip
from ..InternalProtocol.weather import Weather
from ..InternalProtocol.station import Station


class FilterWorker():
    def __init__(self):
        self.weathers = {}
        self.stations = {}

    def process_trip(self, trip):
        prec_filter = PrecipitationFilter(trip, self.weathers)
        year_filter = YearFilter(trip, self.weathers)
        mont_filter = MontrealFilter(trip, self.weathers)

        filters = [prec_filter, year_filter, mont_filter]

        values = []

        for filter in filters:
            value = filter.run()
            if value is not None:
                values.append(value)

        return value

    def process_station(self, station: Station):
        station_id = station.get_id()
        self.stations.update({station_id: station})

    def process_weather(self, weather: Weather):
        weather_id = weather.get_id()
        self.weathers.update({weather_id: weather})

    def add_data(self, body_read):
        entity_to_process = read_message(body_read, self.stations)

        is_int = isinstance(entity_to_process, int)
        is_stop = is_int and entity_to_process == STOP_TYPE

        if isinstance(entity_to_process, Trip):
            values = self.process_trip(entity_to_process)
            return values
        elif isinstance(entity_to_process, Station):
            self.process_station(entity_to_process)
            return None
        elif isinstance(entity_to_process, Weather):
            self.process_weathers(entity_to_process)
            return None
        elif is_stop:
            return [(STOP_TYPE, [])]
        else:
            ent_type = type(entity_to_process)
            raise Exception(f"Type Received Don't Make Sense {ent_type}")
