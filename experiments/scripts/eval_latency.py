import os
import argparse
import numpy as np
import pandas as pd
from datetime import timedelta, datetime


def compute_latency(input_dir: str):
    df_res = None
    assert os.path.exists(input_dir), 'invalid input directory'
    for t in range(1, 6):
        print('computing latency for sample ', t)
        lidar_file = os.path.join(input_dir, "lidar_{}.csv".format(t))
        assert os.path.exists(lidar_file), 'lidar file not found'
        palicus_file = os.path.join(input_dir, "palicus_{}.csv".format(t))
        assert os.path.exists(palicus_file), 'palicus file not found'
        output_file = "latency_{}.csv".format(t)
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
            frame_latencies.append([t, f, latency_ms])

        df_res_t = pd.DataFrame(np.array(frame_latencies), columns=['sample', 'frame_nr', 'latency [ms]'])
        df_res_t.to_csv(output_file_path, index=False)
        print('\t done')
        # global result
        if df_res is None:
            df_res = df_res_t
        else:
            df_res = pd.concat([df_res, df_res_t])

    df_res = df_res.groupby('frame_nr').mean()['latency [ms]']
    output_file_path = os.path.join(input_dir, "latency.csv")
    df_res.to_csv(output_file_path, index=True)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--input-dir", metavar="input_dir", required=True,
                            help="Input directory containing the traffic_data")

    args = arg_parser.parse_args()
    compute_latency(args.input_dir)
