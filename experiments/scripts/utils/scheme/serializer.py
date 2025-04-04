from ..constants import N_FEATURES

scheme = {"type": "object",
          "properties": {
              "items_per_packet": {"type": "integer"},
              "features_per_item": {"type": "integer"},
              "feature_indices": {"type": "array",
                                  "items": {"type": "integer"},
                                  "minItems": 1,
                                  "maxItems": N_FEATURES
                                  }
          },
          "required": ["items_per_packet", "features_per_item", "feature_indices"]
          }
