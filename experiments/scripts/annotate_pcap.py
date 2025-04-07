import os
import argparse
from pcapkit import extract
import pandas as pd

from utils import annotate_lidar_packet, annotate_palicus_packet

LIDAR_IP = '192.168.1.201'
PALICUS_IP = '192.168.88.202'

def annotate_pacp_traffic(input_file: str, output_dir: str, palicus_ip:str, lidar_ip:str, delta_phi:float):
    assert os.path.exists(input_file) and os.path.isfile(input_file) and input_file.endswith('.pcap'), 'invalid input file'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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
                log, curr_lidar_frame, curr_lidar_azimuth = annotate_lidar_packet(f, packet_nr, curr_lidar_frame, delta_phi, curr_lidar_azimuth)
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
        lidar_data.sort_values(by=['frame_nr', 'pkt_nr'], inplace=True)
        lidar_data.reset_index(drop=True)
        lidar_data.to_csv(os.path.join(output_dir, 'lidar.csv'), index=False)
    if palicus_data is not None:
        palicus_data.sort_values(by=['frame_nr', 'pkt_nr'], inplace=True)
        palicus_data.reset_index(drop=True)
        palicus_data.to_csv(os.path.join(output_dir, 'palicus.csv'), index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", metavar='input_file', required=True,
                        help="path to the input file")
    parser.add_argument("--output-dir", metavar='output_dir', required=True,
                        help="directory to store the result")
    parser.add_argument("--lidar-ip", metavar='lidar_ip', required=False, default=LIDAR_IP)
    parser.add_argument("--palicus-ip", metavar='palicus_ip', required=False, default=PALICUS_IP)
    parser.add_argument('--delta-phi', metavar='delta_phi', default=0.1,
                        help='horizontal angular resolution of the captured data if source == lidar')

    args = parser.parse_args()
    annotate_pacp_traffic(args.input_file, args.output_dir, args.palicus_ip, args.lidar_ip, args.delta_phi)
