import os
import argparse
import numpy as np
import pandas as pd
from datetime import timedelta, datetime


def compute_latency(input_dir: str, output_file: str):
    assert os.path.exists(input_dir), 'invalid input directory'
    lidar_file = os.path.join(input_dir, "lidar.csv")
    assert os.path.exists(lidar_file), 'lidar file not found'
    palicus_file = os.path.join(input_dir, "palicus.csv")
    assert os.path.exists(palicus_file), 'palicus file not found'

    output_file_path = os.path.join(input_dir, output_file)

    lidar_data = pd.read_csv(lidar_file)
    palicus_data = pd.read_csv(palicus_file)
    n_frames = min(lidar_data.max()['frame_nr'] + 1, palicus_data.max()['frame_nr'] + 1)
    frame_latencies = []
    for f in range(int(n_frames)):
        # associate palicus frame [f_src] with lidar frame [f_tar]
        palicus_packets = palicus_data.loc[palicus_data['frame_nr'] == f]
        palicus_timestamp = palicus_packets.max()['timestamp']
        palicus_timestamp = datetime.strptime(palicus_timestamp, '%Y-%m-%d %H:%M:%S.%f')

        lidar_packets = lidar_data.loc[lidar_data['frame_nr'] == f]
        lidar_timestamp = lidar_packets.max()['timestamp']
        lidar_timestamp = datetime.strptime(lidar_timestamp, '%Y-%m-%d %H:%M:%S.%f')

        latency = timedelta(
            hours=palicus_timestamp.hour - lidar_timestamp.hour,
            minutes=palicus_timestamp.minute - lidar_timestamp.minute,
            seconds=palicus_timestamp.second - lidar_timestamp.second,
            microseconds=palicus_timestamp.microsecond - lidar_timestamp.microsecond
        )
        latency_ms = (latency.seconds * (10 ** 3) + latency.microseconds * (10 ** -3))
        frame_latencies.append([f, latency_ms])

    df_res = pd.DataFrame(np.array(frame_latencies), columns=['frame_nr', 'latency [ms]'])
    df_res.to_csv(output_file_path, index=False)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--input-dir", metavar="input_dir", required=True,
                            help="Input directory containing the traffic_data")
    arg_parser.add_argument("--output-file", metavar="output_file", required=False, default="latency.csv",
                            help="name of the output file (csv)")

    args = arg_parser.parse_args()
    compute_latency(args.input_dir, args.output_file)
