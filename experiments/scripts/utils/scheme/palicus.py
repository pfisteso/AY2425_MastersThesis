from . import aggregation_unit_scheme, arithmetic_unit_scheme, filter_unit_scheme, serializer_scheme
from ..constants import UNIT_TYPES, N_FILTER_UNITS, N_ARITH_UNITS, N_AGG_UNITS

scheme = {
    'type': 'object',
    'properties': {
        'crossbar': {
            'type': 'array',
            'items': {'enum': UNIT_TYPES},
            'maxItems': N_FILTER_UNITS + N_ARITH_UNITS + N_AGG_UNITS
        },
        'filter': {
            'type': 'array',
            'items': filter_unit_scheme,
            'maxItems': N_FILTER_UNITS
        },
        'arithmetic': {
            'type': 'array',
            'items': arithmetic_unit_scheme,
            'maxItems': N_ARITH_UNITS
        },
        'aggregation': {
            'type': 'array',
            'items': aggregation_unit_scheme,
            'maxItems': N_AGG_UNITS
        },
        # serialization parameters
        'serialize': serializer_scheme
    },
    'required': ['crossbar', 'serialize'],
}
