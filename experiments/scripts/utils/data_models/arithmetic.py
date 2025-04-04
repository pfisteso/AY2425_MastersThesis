from jsonschema import validate
from typing import List

from .utils import zero_pad
from ..constants import ARITH_CELL_CONFIG_LENGTH
from ..constants import ARITHMETIC_OPCODE_MAP, FEATURE_MAP, N_ARITH_CELLS, N_FEATURES
from ..scheme import arithmetic_cell_scheme, arithmetic_unit_scheme

class ArithmeticCell:
    use_reg: bool
    signed: bool
    opcode: int
    idx_0: int
    idx_1: int
    register: int

    def __init__(self, **kwargs):
        validate(kwargs, arithmetic_cell_scheme)
        self.use_reg = kwargs['use_reg']
        self.signed = kwargs['signed']
        self.opcode = ARITHMETIC_OPCODE_MAP[kwargs['opcode']]

        ftr = kwargs['feature_0']
        if isinstance(ftr, str):
            assert ftr in FEATURE_MAP, 'invalid feature [0]'
            ftr = FEATURE_MAP[ftr]
        assert ftr < N_FEATURES, 'invalid feature idx [0]'
        self.idx_0 = ftr

        if self.use_reg:
            assert 'register' in kwargs
            self.register = kwargs['register']
            self.idx_1 = 0
        else:
            assert 'feature_1' in kwargs
            self.register = 0
            ftr = kwargs['feature_1']
            if isinstance(ftr, str):
                assert ftr in FEATURE_MAP, 'invalid feature [1]'
                ftr = FEATURE_MAP[ftr]
            assert ftr < N_FEATURES, 'invalid feature idx [1]'
            self.idx_1 = ftr


    def get_config_bytes(self) -> bytearray:
        # opcode
        op_int = self.opcode
        if self.signed:
            op_int += 4
        if self.use_reg:
            op_int += 16
        opcode_byte = op_int.to_bytes(1, byteorder='big')
        print("Arithmetic Cell")
        print('\t opcode: ', opcode_byte.hex())

        res = bytearray(opcode_byte)
        # feature 0, feature 1
        f_idx_int = self.idx_0 + 16 * self.idx_1
        f_idx_byte = f_idx_int.to_bytes(1, byteorder='big')
        print('\t f_idx: ', f_idx_byte.hex())
        res.extend(f_idx_byte)
        # register
        register_bytes = self.register.to_bytes(2, byteorder='big', signed=self.signed)
        print('\t register: ', register_bytes.hex())
        res.extend(register_bytes)
        return res

class ArithmeticUnit:
    cells: List[ArithmeticCell]
    output_features: List[int]

    def __init__(self, **kwargs):
        validate(kwargs, arithmetic_unit_scheme)
        cells = kwargs['cells']
        assert len(cells) <= N_ARITH_CELLS
        self.cells = [ArithmeticCell(**cell) for cell in cells]

        assert len(kwargs['output_features']) <= N_FEATURES
        self.out_features = kwargs['output_features']
        while len(self.out_features) < N_FEATURES:
            self.out_features.append(0)
        if len(self.out_features) % 2 == 1:
            self.out_features.append(0)

    def get_config_bytes(self) -> bytearray:
        res = bytearray()
        # unit config
        unit_bytes = bytearray()
        i = 0
        while 2 * i + 1 < len(self.out_features):
            ftr_byte = int(self.out_features[2 * i] * 16 + self.out_features[2 * i + 1])
            unit_bytes.extend(ftr_byte.to_bytes(1, byteorder='big'))
            i += 1
        print("Arithmetic Unit - output features: ", unit_bytes.hex())
        res.extend(unit_bytes)


        # cell config
        cell_bytes = bytearray()
        for cell in self.cells:
            cell_bytes.extend(cell.get_config_bytes())
        zero_pad(cell_bytes, N_ARITH_CELLS * ARITH_CELL_CONFIG_LENGTH)
        res.extend(cell_bytes)
        return res
