import os
import argparse
import pandas as pd
from typing import List
from pcapkit import extract

PALICUS_IP = '192.168.88.202'


def eval_frame_size(directory: str, throughput: List[int], palicus_ip: str, n_ftrs: int, experiment: str,
                    reload: bool = False):
    assert os.path.exists(directory), 'invalid input directory'
    log_path = os.path.join(directory, 'frame_size_log.csv')

    if reload or not os.path.exists(log_path):
        result = []
        for t in throughput:
            print(t, ' Mbps...')
            filename = 'traffic_{}.pcap'.format(t)
            filepath = os.path.join(directory, filename)
            assert os.path.exists(filepath), 'invalid file {}'.format(filepath)
            data = extract(filepath, nofile=True)
            pkt_nr = 0

            for f in data.frame:
                pkt_nr += 1
                try:
                    ip_src = f.info.ethernet.ipv4.src.exploded
                    if ip_src != palicus_ip:
                        continue
                    payload = f.payload.payload.payload.payload.data
                    frame_nr = int.from_bytes(payload[0:2], byteorder='big', signed=False)
                    n_elements = (len(payload) - 2) // (2 * n_ftrs)  # 2 Bytes for Azimuth, then 2 * n_ftrs per element
                    result.append([t, frame_nr, pkt_nr, n_elements])
                except Exception as e:
                    print('Error: ', str(e))
            print('\t done')

        df_res = pd.DataFrame(result, columns=['throughput', 'frame_nr', 'pkt_nr', 'n_elements'])
        df_res.to_csv(os.path.join(directory, 'frame_size_log.csv'), index=False)

    else:
        df_res = pd.read_csv(log_path)

    df_res = df_res.groupby(['throughput', 'frame_nr']).sum().reset_index(drop=False).loc[:,
             ['throughput', 'frame_nr', 'n_elements']]
    if experiment == 'point_rate':
        total = pd.DataFrame(df_res.groupby(['throughput']).sum()).reset_index(drop=False)
        total['frame_nr'] = 'TOTAL'
        total = total.loc[:, ['throughput', 'frame_nr', 'n_elements']]
        df_res = pd.concat([df_res, total], axis=0)
    else:  # 'latency'
        df_res = df_res.groupby('frame_nr').mean().reset_index(drop=False).loc[:, ['frame_nr', 'n_elements']]
    df_res.to_csv(os.path.join(directory, 'frame_size.csv'), index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--experiment', required=True)
    parser.add_argument('--palicus_ip', required=False, default=PALICUS_IP)
    parser.add_argument('--n-ftrs', required=False, type=int, default=3)
    parser.add_argument('--reload', required=False, type=bool, default=False)

    args = parser.parse_args()
    input_dir = args.input_dir

    assert args.experiment in ['latency', 'point_rate'], 'invalid experiment {}'.format(args.experiment)

    throughput = [1, 2, 3, 4, 5] if args.experiment == 'latency' else [8, 16, 32, 64]  # ToDo: 128

    eval_frame_size(input_dir, throughput=throughput, palicus_ip=args.palicus_ip, n_ftrs=args.n_ftrs,
                    experiment=args.experiment, reload=args.reload)
