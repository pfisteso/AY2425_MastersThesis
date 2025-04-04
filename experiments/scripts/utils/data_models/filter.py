from typing import List
from jsonschema import validate

from ..scheme import filter_unit_scheme, filter_cell_scheme
from ..constants import N_FILTER_CELLS, FILTER_CELL_OPCODES_MAP, FILTER_UNIT_OPCODE_MAP, FEATURE_MAP, FILTER_CELL_CONFIG_LENGTH
from .utils import zero_pad

class FilterCell:
    active: bool
    feature_idx: int
    signed: bool
    opcode: int
    register: int



    def __init__(self, **kwargs):
        validate(kwargs, filter_cell_scheme)
        self.active = kwargs['active']
        if not self.active:
            self.feature_idx = 0
            self.signed = False
            self.opcode = 0
            self.register = 0

        else:
            # assert kwargs
            assert 'opcode' in kwargs
            assert 'signed' in kwargs
            assert 'register' in kwargs
            assert 'feature' in kwargs

            opc_string = kwargs['opcode']
            self.opcode = FILTER_CELL_OPCODES_MAP[opc_string]

            self.signed = kwargs['signed']

            ftr = kwargs['feature']
            if isinstance(ftr, str):
                assert ftr in FEATURE_MAP, 'invalid feature'
                ftr = FEATURE_MAP[ftr]
            assert ftr < 7, 'invalid feature index'
            self.feature_idx = ftr

            self.register = kwargs['register']

    def get_config_bytes(self) -> bytearray:
        if not self.active:
            return bytearray(int(0).to_bytes(4, byteorder='big'))
        opcode = self.opcode + 16
        if self.signed:
            opcode += 8
        opcode_byte = opcode.to_bytes(1, byteorder='big')
        feature_idx_byte = self.feature_idx.to_bytes(1, byteorder='big')
        register_bytes = self.register.to_bytes(2, byteorder='big', signed=self.signed)
        res = bytearray(opcode_byte)
        res.extend(feature_idx_byte)
        res.extend(register_bytes)

        print('Filter Cell:')
        print('\topcode:\t', opcode_byte.hex())
        print('\tfeature:\t', feature_idx_byte.hex())
        print('\tregister:\t', register_bytes.hex())

        return res



class FilterUnit:
    active: bool
    opcode: int
    cells: List[FilterCell]

    def __init__(self, **kwargs):
        validate(kwargs, filter_unit_scheme)

        self.active = kwargs['active']
        if not self.active:
            self.opcode = 0
            self.cells = []

        else:
            assert 'opcode' in kwargs
            opc_str = kwargs['opcode']
            self.opcode = FILTER_UNIT_OPCODE_MAP[opc_str]

            cells = kwargs['cells'] if 'cells' in kwargs else []
            assert len(cells) <= N_FILTER_CELLS
            self.cells = [FilterCell(**cells[i]) for i in range(len(cells))]

    def get_config_bytes(self) -> bytearray:
        res = bytearray(self.opcode.to_bytes(1, byteorder='big', signed=False))
         # parse cells
        cell_bytes = bytearray()
        for cell in self.cells:
            cell_bytes.extend(cell.get_config_bytes())
        zero_pad(cell_bytes, N_FILTER_CELLS * FILTER_CELL_CONFIG_LENGTH)
        res.extend(cell_bytes)
        return res