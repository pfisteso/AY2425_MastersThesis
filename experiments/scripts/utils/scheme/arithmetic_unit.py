from . import arithmetic_cell_scheme
from ..constants import N_ARITH_CELLS, N_FEATURES

scheme = {
    'type': 'object',
    'properties': {
        'cells': {
            'type': 'array',
            'items': arithmetic_cell_scheme,
            'maxItems': N_ARITH_CELLS
        },
        'output_features': {
            'type': 'array',
            'items': {'type': 'integer'},
            'maxItems': N_FEATURES
        }
    },
    'required': ['cells', 'output_features']
}
