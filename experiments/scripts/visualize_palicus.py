import argparse

from utils.constants import PALICUS_IP
from utils import load_palicus_frame, visualize2d, visualize3d


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcap-file', required=True)
    parser.add_argument('--frame-nr', required=True,  type=int)
    parser.add_argument("--palicus-ip", required=False, default=PALICUS_IP)
    parser.add_argument('--dimensionality', required=False, type=int, default=2)
    parser.add_argument("--scale-x", required=False, type=float, default=1 / 250)
    parser.add_argument("--scale-y", required=False, type=float,  default=1 / 250)
    parser.add_argument("--scale-z", required=False, type=float,  default=1 / 250)
    parser.add_argument('--signed-x', required=False, type=bool,  default=True)
    parser.add_argument('--signed-y', required=False, type=bool, default=True)
    parser.add_argument('--signed-z', required=False, type=bool, default=True)
    parser.add_argument('--flip-img', required=False, type=bool, default=False)

    args = parser.parse_args()

    assert int(args.dimensionality) in [2, 3], "invalid dimensionality"

    ftrs = ['x', 'y', 'z'] if int(args.dimensionality) == 3 else ['px', 'py', 'color']
    ftr_factors = [float(args.scale_x), float(args.scale_y), float(args.scale_z)]
    ftrs_signed = [bool(args.signed_x), bool(args.signed_y), bool(args.signed_z)]

    parsed_data = load_palicus_frame(input_file=args.pcap_file, ip=args.palicus_ip, frame_nr=args.frame_nr,
                                     columns=ftrs, scales=ftr_factors, signed=ftrs_signed)

    if int(args.dimensionality) == 2:
        visualize2d(parsed_data, flip_img=bool(args.flip_img))
    else:
        visualize3d(parsed_data)
