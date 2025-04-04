import os
import argparse

from utils import annotate_lidar_pcap

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-path", metavar='file_path', required=True,
                        help="path to the input file")
    parser.add_argument("--output-file", metavar='output_path', required=True,
                        help="file to store the result")
    parser.add_argument("--source", metavar='source', default='lidar',
                        help='data source: palicus or lidar')
    parser.add_argument('--delta-phi', metavar='delta_phi', default=0.1,
                        help='horizontal angular resolution of the captured data if source == lidar')

    args = parser.parse_args()
    file_path = args.file_path
    output_file = args.output_file
    source = args.source

    assert source in ('palicus', 'lidar'), 'invalid source'
    assert os.path.exists(file_path) and file_path.endswith('.pcap'), 'invalid input file'

    if source == 'lidar':
        annotate_lidar_pcap(file_path, output_file, delta_alpha=args.delta_phi)
    else:
        pass