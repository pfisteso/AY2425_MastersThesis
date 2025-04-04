from . import filter_cell_scheme
from ..constants import FILTER_UNIT_OPCODE_STRINGS, N_FILTER_CELLS


scheme = {
    'type': 'object',
    'properties': {
        'active': {'type': 'boolean'},
        'opcode': {'enum': FILTER_UNIT_OPCODE_STRINGS},
        'cells': {
            'type': 'array',
            'items': filter_cell_scheme,
            'maxItems': N_FILTER_CELLS
        }
    },
    'required': ['active']
}