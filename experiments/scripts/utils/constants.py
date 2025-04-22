import math

# --- NETWORKING CONSTANTS --- #
PALICUS_IP = '192.168.88.202'
LIDAR_IP = '192.168.1.201'
HOST_IP = '192.168.88.2'
DATA_PORT = 2368
CONFIG_PORT = 1234
# I_FACE = 'enx349971d694ea'  # home
I_FACE = 'enx349971012345'  # office

# --- SYSTEM CONSTANTS --- #
MODE_POINT_CLOUD = 'CLOUD'
MODE_VOXEL = 'VOXEL'
MODE_FRONTAL_VIEW = 'FV'
MODE_BIRDS_EYE_VIEW = 'BEV'
MODES = [MODE_POINT_CLOUD, MODE_VOXEL, MODE_FRONTAL_VIEW, MODE_BIRDS_EYE_VIEW]

# --- FEATURES --- #
N_FEATURES = 7

FEATURE_STRING = ['x', 'y', 'z', 'r', 'a', 'w', 'i']
SIGNED_FEATURES = ['x', 'y', 'z', 'i']
FEATURE_MAP = {'x': 0,
               'y': 1,
               'z': 2,
               'r': 3,
               'a': 4,
               'w': 5,
               'i': 6
               }
FTR_FACTOR = {'x': 1000 / 4,
              'y': 1000 / 4,
              'z': 1000 / 4,
              'r': 1000 / 2,
              'a': 100,
              'w': 1,
              'i': 1
}

R_MIN = 0
R_MAX = 100
W_MIN = -15
W_MAX = 15
A_MIN = 0
A_MAX = 360.0

FTR_LOWER_BOUNDS = {
    'x': R_MAX * -1 * FTR_FACTOR['x'],
    'y': R_MAX * -1 * FTR_FACTOR['y'],
    'z': R_MAX * math.sin(math.radians(W_MIN)) * FTR_FACTOR['z'],
    'r': R_MIN * FTR_FACTOR['r'],
    'a': A_MIN * FTR_FACTOR['a'],
    'w': W_MIN * FTR_FACTOR['w'],
    'i': 0 * FTR_FACTOR['i']
}

FTR_UPPER_BOUNDS = {
    'x': R_MAX * FTR_FACTOR['x'],
    'y': R_MAX * FTR_FACTOR['y'],
    'z': R_MAX * math.sin(math.radians(W_MAX)) * FTR_FACTOR['z'],
    'r': R_MAX * FTR_FACTOR['r'],
    'a': A_MAX * FTR_FACTOR['a'],
    'w': W_MAX * FTR_FACTOR['w'],
    'i': 255 * FTR_FACTOR['i']
}

# --- FILTERING --- #
UNIT_TYPE_FILTER = 'FILTER'
N_FILTER_UNITS = 3
N_FILTER_CELLS = 6
FILTER_CELL_CONFIG_LENGTH = 4
FILTER_UNIT_CONFIG_LENGTH = 1 + N_FILTER_CELLS * FILTER_CELL_CONFIG_LENGTH

FILTER_UNIT_OPCODE_STRINGS = ['OR', 'AND', 'NOR', 'NAND']
FILTER_UNIT_OPCODE_MAP = {
    'OR': 0,
    'AND': 1,
    'NOR': 2,
    'NAND': 3
}
FILTER_CELL_OPCODE_STRING = ['le', 'leq', 'eq', 'ne', 'ge', 'gt', 'geq']
FILTER_CELL_OPCODES_MAP = {'le': 0,
                           'leq': 6,
                           'eq': 1,
                           'ne': 5,
                           'geq': 4,
                           'gt': 2}

# --- ARITHMETICAL OPERATIONS --- #
UNIT_TYPE_ARITH = 'ARITH'
N_ARITH_UNITS = 3
N_ARITH_CELLS = 3
ARITH_CELL_CONFIG_LENGTH = 4
ARITH_UNIT_CONFIG_LENGTH = 4 + N_ARITH_CELLS * ARITH_CELL_CONFIG_LENGTH

ARITHMETIC_OPCODE_STRINGS = ['add', 'sub', 'div']
ARITHMETIC_OPCODE_MAP = {'add': 0,
                         'sub': 1,
                         'div': 3}

# AGGREGATION
UNIT_TYPE_AGG = 'AGG'
N_AGG_UNITS = 1
N_AGG_INDICES = 3
N_AGG_CELLS = N_FEATURES - N_AGG_INDICES

AGG_CELL_CONFIG_LENGTH = 1
AGG_UNIT_CONFIG_LENGTH = 4 + N_AGG_CELLS * AGG_CELL_CONFIG_LENGTH

AGGREGATION_OPCODE_STRING = ['min', 'max', 'mean']
AGGREGATION_OPCODE_MAP = {'min': 2,
                          'max': 3,
                          'mean': 1}

# SERIALIZATION
N_OUTPUT_FEATURES = 3


UNIT_TYPES = [UNIT_TYPE_FILTER, UNIT_TYPE_ARITH, UNIT_TYPE_AGG]