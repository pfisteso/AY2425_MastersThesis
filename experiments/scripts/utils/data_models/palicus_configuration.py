from typing import List
from jsonschema import validate

from . import Crossbar, FilterUnit, ArithmeticUnit, AggregationUnit
from .serializer import Serializer
from .utils import zero_pad

from ..scheme import palicus_config_scheme
from ..constants import N_FILTER_UNITS, N_ARITH_UNITS, N_AGG_UNITS, FILTER_UNIT_CONFIG_LENGTH, ARITH_UNIT_CONFIG_LENGTH, AGG_UNIT_CONFIG_LENGTH


class PalicusConfiguration:

    cb: Crossbar
    filter: List[FilterUnit]
    arithmetic: List[ArithmeticUnit]
    aggregation: List[AggregationUnit]
    serializer: Serializer

    def __init__(self, **kwargs):
        validate(kwargs, palicus_config_scheme)
        # crossbar
        self.cb = Crossbar(unit_order=kwargs['crossbar'])

        # filter units
        self.filter = []
        filter_configs = kwargs['filter'] if 'filter' in kwargs else []
        assert len(filter_configs) <= N_FILTER_UNITS
        for f in filter_configs:
            if f['active']:
                self.filter.append(FilterUnit(**f))

        # arithmetic units
        self.arithmetic = []
        arith_config = kwargs['arithmetic'] if 'arithmetic' in kwargs else []
        assert len(arith_config) <= N_ARITH_UNITS
        for arith in arith_config:
            self.arithmetic.append(ArithmeticUnit(**arith))

        # aggregation unit
        self.aggregation = []
        agg_config = kwargs['aggregation'] if 'aggregation' in kwargs else []
        assert len(agg_config) <= N_AGG_UNITS
        for agg in agg_config:
            self.aggregation.append(AggregationUnit(**agg))

        # serialization parameters
        self.serializer = Serializer(**kwargs['serialize'])

        self.validate()

    def get_config_bytes(self):
        self.validate()

        res = self.cb.get_config_bytes()

        filter_bytes = bytearray()
        for f in self.filter:
            filter_bytes.extend(f.get_config_bytes())
        zero_pad(filter_bytes, N_FILTER_UNITS * FILTER_UNIT_CONFIG_LENGTH)
        res.extend(filter_bytes)

        arith_bytes = bytearray()
        for arith in self.arithmetic:
            arith_bytes.extend(arith.get_config_bytes())
        zero_pad(arith_bytes, N_ARITH_UNITS * ARITH_UNIT_CONFIG_LENGTH)
        res.extend(arith_bytes)

        agg_bytes = bytearray()
        for agg in self.aggregation:
            agg_bytes.extend(agg.get_config_bytes())
        zero_pad(agg_bytes, N_AGG_UNITS * AGG_UNIT_CONFIG_LENGTH)
        res.extend(agg_bytes)

        res.extend(self.serializer.get_config_bytes())

        # store_config(res)
        return res

    def validate(self):
        assert len(self.filter) <= N_FILTER_UNITS
        assert len(self.arithmetic) <= N_ARITH_UNITS
        assert len(self.aggregation) <= N_AGG_UNITS

def store_config(config_bytes: bytearray):
    as_string = config_bytes.hex()
    as_array = []
    i = 0
    while (i+1) < len(as_string):
        as_array.append(as_string[i:i+2])
        i += 2
    as_string = '\n'.join(as_array)
    as_string = as_string.replace('0', '0000')
    as_string = as_string.replace('1', '0001')
    as_string = as_string.replace('2', '0010')
    as_string = as_string.replace('3', '0011')
    as_string = as_string.replace('4', '0100')
    as_string = as_string.replace('5', '0101')
    as_string = as_string.replace('6', '0110')
    as_string = as_string.replace('7', '0111')
    as_string = as_string.replace('8', '1000')
    as_string = as_string.replace('9', '1001')
    as_string = as_string.replace('a', '1010')
    as_string = as_string.replace('b', '1011')
    as_string = as_string.replace('c', '1100')
    as_string = as_string.replace('d', '1101')
    as_string = as_string.replace('e', '1110')
    as_string = as_string.replace('f', '1111')

    with open('./logs/palicus.txt', 'w') as f:
        f.write(as_string)
