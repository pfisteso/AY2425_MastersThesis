import math
from typing import List

from ..constants import N_FILTER_UNITS, N_ARITH_UNITS, N_AGG_UNITS
from ..constants import UNIT_TYPE_FILTER, UNIT_TYPE_ARITH, UNIT_TYPE_AGG

CROSSBAR_DIM = N_FILTER_UNITS + N_ARITH_UNITS + N_AGG_UNITS + 1

class Crossbar:

    unit_order: List[str]
    crossbar: List[int]

    def __init__(self, unit_order: List[str]):
        self.unit_order = unit_order
        self._parse_crossbar()
        assert len(self.crossbar) == CROSSBAR_DIM

    def get_config_bytes(self) -> bytearray:
        res = bytearray()
        print(self.crossbar)
        for c in self.crossbar:
            res.extend(c.to_bytes(length=1, byteorder='big', signed=False))
        assert len(res) == CROSSBAR_DIM
        return res

    def _parse_crossbar(self):
        self.crossbar = [0 for _ in range(CROSSBAR_DIM)]

        # parse the crossbar-config from the unit order
        nxt_byte = 128
        nxt_filter = 1
        nxt_arith = 8
        nxt_agg = 64

        for unit in self.unit_order:
            if unit == UNIT_TYPE_FILTER:
                idx = int(math.log2(nxt_filter))

                if idx >= N_FILTER_UNITS:
                    raise Exception("too many filter units")

                self.crossbar[idx] = nxt_byte
                nxt_byte = nxt_filter
                nxt_filter *= 2
                continue

            if unit == UNIT_TYPE_ARITH:
                idx = int(math.log2(nxt_arith))
                if idx > N_FILTER_UNITS + N_ARITH_UNITS:
                    raise Exception("too many arith units")
                self.crossbar[idx] = nxt_byte
                nxt_byte = nxt_arith
                nxt_arith *= 2
                continue

            if unit == UNIT_TYPE_AGG:
                idx = int(math.log2(nxt_agg))
                if idx >= N_FILTER_UNITS + N_ARITH_UNITS + N_AGG_UNITS:
                    raise Exception("too many agg units")
                self.crossbar[idx] = nxt_byte
                nxt_byte = nxt_agg
                nxt_agg *= 2
                continue

        # connect to the output
        self.crossbar[CROSSBAR_DIM - 1] = nxt_byte