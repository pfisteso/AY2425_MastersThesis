from typing import List
from jsonschema import validate

from .utils import zero_pad
from ..scheme import aggregation_unit_scheme, aggregation_cell_scheme
from ..constants import SIGNED_FEATURES, FEATURE_MAP, N_AGG_INDICES, N_FEATURES, AGG_CELL_CONFIG_LENGTH, AGGREGATION_OPCODE_MAP


class AggregationCell:
    signed: bool
    opcode: int
    feature_index: int

    def __init__(self, **kwargs):
        validate(kwargs, aggregation_cell_scheme)

        self.opcode = AGGREGATION_OPCODE_MAP[kwargs['opcode']]
        self.signed = kwargs['signed']

        ftr = kwargs['feature']
        if isinstance(ftr, str):
            assert ftr in FEATURE_MAP, 'invalid feature {}'.format(ftr)
            ftr = FEATURE_MAP[ftr]
        assert ftr < N_FEATURES, 'invalid feature index {}'.format(ftr)
        self.feature_index = ftr

    def get_config_bytes(self) -> bytearray:
        res = bytearray()
        opcode_int = self.opcode + 4 if self.signed else self.opcode
        config_byte = int(16 * opcode_int + self.feature_index).to_bytes(1, byteorder='big', signed=False)
        res.extend(config_byte)
        print('\t Aggregation Cell: ', config_byte.hex())
        return res


class AggregationUnit:
    n_idx: int
    group_indices: List[int]
    cells: List[AggregationCell]
    output_feature_indices: List[int]

    def __init__(self, **kwargs):
        validate(kwargs, aggregation_unit_scheme)
        self.n_idx = kwargs['n_idx']
        # group indices
        assert len(kwargs['group_indices']) <= N_AGG_INDICES
        self.group_indices = kwargs['group_indices']
        while len(self.group_indices) < N_AGG_INDICES:
            self.group_indices.append(0)
        # cells
        assert len(kwargs['cells']) <= N_FEATURES
        self.cells = [AggregationCell(**c) for c in kwargs['cells']]

        # output features
        assert len(kwargs['output_feature_indices']) <= N_FEATURES
        self.output_feature_indices = kwargs['output_feature_indices']
        while len(self.output_feature_indices) < N_FEATURES:
            self.output_feature_indices.append(N_FEATURES)
        if len(self.output_feature_indices) % 2 == 1:
            self.output_feature_indices.append(0)

    def get_config_bytes(self):
        idx_byte_0 = int(self.n_idx * 16 + self.group_indices[0]).to_bytes(1, byteorder='big', signed=False)
        idx_byte_1 = int(self.group_indices[1] * 16 + self.group_indices[2]).to_bytes(1, byteorder='big', signed=False)

        unit_bytes = bytearray(idx_byte_0)
        unit_bytes.extend(bytearray(idx_byte_1))
        print('Aggregation Unit: ')
        print('index config: ', unit_bytes.hex())
        output_bytes = bytearray()
        i = 0
        while 2 * i + 1 < len(self.output_feature_indices):
            as_int = self.output_feature_indices[2*i] * 16 + self.output_feature_indices[2*i+1]
            output_bytes.extend(as_int.to_bytes(1, byteorder='big', signed=False))
            i += 1
        # cell configurations
        print('output features: ', output_bytes.hex())
        unit_bytes.extend(output_bytes)
        cell_bytes = bytearray()
        for cell in self.cells:
            cell_bytes.extend(cell.get_config_bytes())
        zero_pad(cell_bytes, N_FEATURES * AGG_CELL_CONFIG_LENGTH)
        unit_bytes.extend(cell_bytes)
        return unit_bytes
