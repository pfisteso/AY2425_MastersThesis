import os
import argparse
import pandas as pd
from typing import List
from pcapkit import extract

from utils.constants import PALICUS_IP


def eval_frame_size(directory: str, throughput: List[int], palicus_ip: str, n_ftrs: int):
    assert os.path.exists(directory), 'invalid input directory'

    for t in throughput:
        result = []
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
                result.append([frame_nr, pkt_nr, n_elements])
            except Exception as e:
                print('Error: ', str(e))
        print('\t done')
        df_res = pd.DataFrame(result)
        df_res = pd.DataFrame(result, columns=['frame_nr', 'pkt_nr', 'n_elements'])
        df_res = df_res.groupby('frame_nr').sum().reset_index(drop=False).loc[:, ['frame_nr', 'n_elements']]
        df_res.to_csv(os.path.join(directory, 'frame_size_{}.csv'.format(t)), index=False)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)

    parser.add_argument('--palicus_ip', required=False, default=PALICUS_IP)
    parser.add_argument('--n-ftrs', required=False, type=int, default=3)

    args = parser.parse_args()
    input_dir = args.input_dir

    throughput =  [8, 16, 32, 64, 128]

    eval_frame_size(input_dir, throughput=throughput, palicus_ip=args.palicus_ip, n_ftrs=args.n_ftrs)
