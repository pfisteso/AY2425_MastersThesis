import os
import argparse
from pcapkit import extract
import numpy as np
import pandas as pd

from utils import annotate_lidar_packet, annotate_palicus_packet

LIDAR_IP = '192.168.1.201'
PALICUS_IP = '192.168.88.202'

MAX_PKT = 460


def smooth_palicus(palicus_data: pd.DataFrame, max_pkt: int, output_dir: str):
    offset = 0
    packet_map = []
    packet_count = palicus_data.groupby('frame_nr').count().reset_index(drop=False)
    for row in packet_count.itertuples():
        if row.pkt_nr > max_pkt:
            offset += row.pkt_nr // max_pkt
        packet_map.append([row.frame_nr, row.frame_nr + offset])
    pd.DataFrame(np.array(packet_map), columns=['frame_nr', 'maps_to']).to_csv(
        os.path.join(output_dir, 'palicus_frame_map.csv'), index=False)


def annotate_pacp_traffic(input_file: str, output_dir: str, palicus_ip: str, lidar_ip: str, delta_phi: float, max_pkt):
    assert os.path.exists(input_file) and os.path.isfile(input_file) and input_file.endswith(
        '.pcap'), 'invalid input file'
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
        lidar_data.to_csv(os.path.join(output_dir, 'lidar.csv'), index=False)
    if palicus_data is not None:
        palicus_data.to_csv(os.path.join(output_dir, 'palicus.csv'), index=False)
        smooth_palicus(palicus_data, max_pkt, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", metavar='dir', required=True, help='working directory')
    parser.add_argument("--lidar-ip", metavar='lidar_ip', required=False, default=LIDAR_IP)
    parser.add_argument("--palicus-ip", metavar='palicus_ip', required=False, default=PALICUS_IP)
    parser.add_argument('--delta-phi', metavar='delta_phi', default=0.1,
                        help='horizontal angular resolution of the captured lidar data')
    parser.add_argument("--max-palicus-pkt", metavar='max_palicus_pkt', required=False, default=MAX_PKT)

    args = parser.parse_args()
    input_file = os.path.join(args.dir, 'traffic.pcap')

    annotate_pacp_traffic(input_file, args.dir,
                          palicus_ip=args.palicus_ip, lidar_ip=args.lidar_ip,
                          delta_phi=args.delta_phi, max_pkt=int(args.max_palicus_pkt))
    # df_palicus = pd.read_csv(os.path.join(args.output_dir, 'palicus.csv'))
    # smooth_palicus(df_palicus, args.max_palicus_pkt, args.output_dir)
