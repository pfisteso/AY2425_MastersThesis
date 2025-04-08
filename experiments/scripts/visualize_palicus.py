import os
import argparse
import pandas as pd
from pcapkit import extract
from typing import List

from utils import extract_palicus_data, visualize2d, visualize3d

PALICUS_IP = '192.168.88.202'


def parse_palicus_data(filepath: str, ip: str, frame_nr: int, columns: List[str], scales: List[float], signed: List[bool]) -> pd.DataFrame:
    assert os.path.exists(filepath) and os.path.isfile(filepath) and filepath.endswith('.pcap'), 'invalid input file'
    data = extract(filepath, nofile=True)
    frame_data = None

    for f in data.frame:
        try:
            ip_src = f.info.ethernet.ipv4.src.exploded
            if ip_src != ip:
                continue
            valid, continue_, data = extract_palicus_data(f, frame_nr, columns, scales, signed)
            if not continue_:
                break
            if valid:
                if frame_data is None:
                    frame_data = data
                else:
                    frame_data = pd.concat([frame_data, data])
        except Exception as e:
            print('ERROR when parsing packet: ', str(e))
            continue
    return frame_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap-file', required=True)
    parser.add_argument('--frame-nr', required=True)
    parser.add_argument("--palicus-ip", required=False, default=PALICUS_IP)
    parser.add_argument('--dimensionality', required=False, default=2)
    parser.add_argument("--scale-x", required=False, default=250)
    parser.add_argument("--scale-y", required=False, default=250)
    parser.add_argument("--scale-z", required=False, default=250)
    parser.add_argument('--signed-x', required=False, default=True)
    parser.add_argument('--signed-y', required=False, default=True)
    parser.add_argument('--signed-z', required=False, default=True)
    parser.add_argument('--flip-img', required=False, default=False)

    args = parser.parse_args()

    assert int(args.dimensionality) in [2, 3], "invalid dimensionality"

    ftrs = ['x', 'y', 'z'] if int(args.dimensionality) == 3 else ['px', 'py', 'color']
    ftr_factors = [float(args.scale_x), float(args.scale_y), float(args.scale_z)]
    ftrs_signed = [bool(args.signed_x), bool(args.signed_y), bool(args.signed_z)]

    parsed_data = parse_palicus_data(args.pcap_file, args.palicus_ip, int(args.frame_nr), ftrs, ftr_factors, ftrs_signed)

    if int(args.dimensionality) == 2:
        visualize2d(parsed_data, flip_img=bool(args.flip_img))
    else:
        visualize3d(parsed_data)
