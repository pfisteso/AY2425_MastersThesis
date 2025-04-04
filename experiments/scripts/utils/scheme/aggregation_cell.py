from ..constants import FEATURE_STRING, AGGREGATION_OPCODE_STRING

scheme = {"type": "object",
          "properties": {
              "opcode": {"enum": AGGREGATION_OPCODE_STRING},
              "signed": {'type': 'boolean'},
              "feature": {'type': ['string', 'integer']}
          },
          "required": ["opcode", "signed", "feature"]
          }
