from ..constants import ARITHMETIC_OPCODE_STRINGS

scheme = {
    'type': 'object',
    'properties': {
        'use_reg': {'type': 'boolean'},
        'signed': {'type': 'boolean'},
        'opcode': {'enum': ARITHMETIC_OPCODE_STRINGS},
        'feature_0': {'type': ['string', 'integer']},
        'feature_1': {'type': ['string', 'integer']},
        'register': {'type': 'number'},
    },
    'required': ['use_reg', 'signed', 'opcode', 'feature_0']
}