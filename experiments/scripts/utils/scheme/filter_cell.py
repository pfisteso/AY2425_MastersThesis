from ..constants import FEATURE_STRING, FILTER_CELL_OPCODE_STRING

scheme = {'type': 'object',
          'properties': {
              'active': {'type': 'boolean'},
              'feature': {'type': ['string', 'integer']},

              'signed': {'type': 'boolean'},
              'opcode': {'enum': FILTER_CELL_OPCODE_STRING},

              'register': {'type':'number'}
          },
          'required': ['active']
          }
