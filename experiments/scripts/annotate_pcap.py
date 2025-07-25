import os
import argparse
import numpy as np
import pandas as pd
from pcapkit import extract

from utils import annotate_lidar_packet, annotate_palicus_packet
from utils.constants import LIDAR_IP, PALICUS_IP

def annotate_pacp_traffic(input_file: str, output_dir: str, palicus_ip: str, lidar_ip: str, delta_phi: float, t: int):
    assert os.path.exists(input_file), '(1) invalid input file: {}'.format(input_file)
    assert os.path.isfile(input_file), '(2) invalid input file: {}'.format(input_file)
    assert input_file.endswith('.pcap'), '(3) invalid input file: {}'.format(input_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print('Annotating ', input_file)
    data = extract(input_file, nofile=True)
    lidar_data = None
    palicus_data = None
    packet_nr = 0
    curr_lidar_frame = 0
    curr_lidar_azimuth = 0.0
    for f in data.frame:
        packet_nr += 1
        try:
            ip_src = f.info.ethernet.ipv4.src.exploded
            if ip_src == lidar_ip:
                log, curr_lidar_frame, curr_lidar_azimuth = annotate_lidar_packet(f, packet_nr, curr_lidar_frame,
                                                                                  delta_phi, curr_lidar_azimuth)
                if lidar_data is None:
                    lidar_data = log
                else:
                    lidar_data = pd.concat([lidar_data, log])
            elif ip_src == palicus_ip:
                log = annotate_palicus_packet(f, packet_nr)
                if palicus_data is None:
                    palicus_data = log
                else:
                    palicus_data = pd.concat([palicus_data, log])
        except Exception as e:
            print('issue when parsing packet {}:\n'.format(packet_nr), str(e))
    if lidar_data is not None:
        lidar_data.to_csv(os.path.join(output_dir, 'lidar_{}.csv'.format(t)), index=False)
    if palicus_data is not None:
        palicus_data.to_csv(os.path.join(output_dir, 'palicus_{}.csv'.format(t)), index=False)
    print('\t done')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help='path to directory')

    parser.add_argument("--experiment", default='latency')
    parser.add_argument("--lidar-ip", metavar='lidar_ip', required=False, default=LIDAR_IP)
    parser.add_argument("--palicus-ip", metavar='palicus_ip', required=False, default=PALICUS_IP)
    parser.add_argument('--delta-phi', type=float, default=0.1,
                        help='horizontal angular resolution of the captured lidar data')

    args = parser.parse_args()
    if args.experiment == 'latency':
        file_numbers = [i for i in range(1, 4)]
    elif args.experiment == 'throughput':
        file_numbers = [8, 16, 32, 64, 128]
    else:
        raise AssertionError('experiment must be latency or throughput')

    for tfile in file_numbers:
        input_file = os.path.join(args.input_dir, 'traffic_{}.pcap'.format(tfile))

        annotate_pacp_traffic(input_file, args.input_dir,
                              palicus_ip=args.palicus_ip, lidar_ip=args.lidar_ip,
                              delta_phi=args.delta_phi, t=tfile)