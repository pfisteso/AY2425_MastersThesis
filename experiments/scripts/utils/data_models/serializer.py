from jsonschema import validate
from typing import List

from ..scheme import serializer_scheme
from ..constants import N_FEATURES

class Serializer:
    items_per_packet: int
    features_per_item: int
    feature_indices: List[int]

    def __init__(self, **kwargs):
        validate(kwargs, serializer_scheme)
        self.items_per_packet = kwargs['items_per_packet']
        self.features_per_item = kwargs['features_per_item']
        self.feature_indices = kwargs['feature_indices']
        while len(self.feature_indices) < N_FEATURES:
            self.feature_indices.append(0)

    def get_config_bytes(self) -> bytearray:
        print("Serializer")
        print("items_per_packet: ", self.items_per_packet)
        print("features_per_item: ", self.features_per_item)
        print("feature_indices: ", self.feature_indices)
        res = bytearray(self.items_per_packet.to_bytes(length=2, byteorder='big', signed=False))
        res.extend(self.features_per_item.to_bytes(length=1, byteorder='big', signed=False))
        i = 0
        while 2 * i + 1 <= len(self.feature_indices):
            as_int = self.feature_indices[2 * i] * 16
            if 2 * i + 1 < len(self.feature_indices):
                as_int += self.feature_indices[2 * i + 1]
            res.extend(as_int.to_bytes(length=1, byteorder='big', signed=False))
            i += 1
        return res