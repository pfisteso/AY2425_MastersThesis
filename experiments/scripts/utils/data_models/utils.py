from ..constants import FEATURE_STRING


def zero_pad(array: bytearray, length: int):
    assert len(array) <= length
    delta = length - len(array)
    if delta > 0:
        array.extend(int(0).to_bytes(delta, byteorder='big', signed=False))

def get_feature_factor(ftr: str) -> float:
    assert ftr in FEATURE_STRING
    factor = 1.0
    if ftr in ['x', 'y', 'z']:
        factor = 1000.0 / 4.0
    if ftr == 'r':
        factor = 1000.0 / 2.0
    if ftr == 'a':
        factor = 100.0
    return factor