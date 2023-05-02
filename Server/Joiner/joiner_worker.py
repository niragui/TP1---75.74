from average_dict_joiner import AverageDictJoiner
from sum_dict_joiner import SumDictJoiner
from average_joiner import AverageJoiner

from joinerprotocol import YEAR_FILTER
from joinerprotocol import PRECIPITATION_FILTER
from joinerprotocol import MONTREAL_FILTER
from joinerprotocol import read_message
from constants import STOP_TYPE
from joinerserverprotocol import QUERY_TYPE

MIN_QUERY_MONTERAL = 6000

class JoinerWorker():
    def __init__(self):
        prec_joiner = AverageJoiner()
        year_joiner = SumDictJoiner()
        mont_joiner = AverageDictJoiner()
        self.joiners = {}
        self.joiners.update({PRECIPITATION_FILTER: prec_joiner})
        self.joiners.update({YEAR_FILTER: year_joiner})
        self.joiners.update({MONTREAL_FILTER: mont_joiner})
        self.ends_found = 0

    def add_trip(self, body):
        data_type, data = read_message(body)


        if data_type == STOP_TYPE:
            self.ends_found += 1
        elif data_type != QUERY_TYPE:
            if data_type not in self.joiners:
                keys = list(self.joiners.keys())
                raise Exception(f"Provided {data_type} and is not in {keys}")
            joiner = self.joiners.get(data_type)
            joiner.update(data)

        return data_type

    def has_finished(self, total_filters):
        return self.ends_found >= total_filters

    def get_montreal_values(self, values):
        aux = []

        for station, average in values.items():
            if average > MIN_QUERY_MONTERAL:
                aux.append(station)

        return aux

    def get_year_values(self, values):
        aux = []

        for station, sum in values.items():
            if sum >= 0:
                aux.append(station)

        return aux

    def get_values(self):
        values = {}

        for key, joiner in self.joiners:
            value = joiner.get_value()
            if key == MONTREAL_FILTER:
                value = self.get_montreal_values(value)
            elif key == YEAR_FILTER:
                value = self.get_year_values(value)
            values.update({key: value})

        return values