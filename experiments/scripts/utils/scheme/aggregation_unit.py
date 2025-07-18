from . import aggregation_cell_scheme
from ..constants import N_AGG_CELLS, N_AGG_INDICES

scheme = {
    'type': 'object',
    'properties': {
        'n_idx': {'type': 'integer'},
        'group_indices': {
            'type': 'array',
            'items': {'type': 'integer'},
            'maxItems': N_AGG_INDICES
        },
        'cells': {
            'type': 'array',
            'items': aggregation_cell_scheme,
            'minItems': 1,
            'maxItems': N_AGG_CELLS
        },
        'output_feature_indices': {
            'type': 'array',
            'items': {'type': 'integer'},
            'minItems': 1,
            'maxItems': N_AGG_CELLS
        }
    },
    'required': ['n_idx', 'group_indices', 'cells', 'output_feature_indices']
}
