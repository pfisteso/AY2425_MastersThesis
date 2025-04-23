import os
import argparse
import pandas  as pd

from pcapkit import extract
from typing import List
from utils import load_palicus_data
from utils.constants import PALICUS_IP


def parse_palicus_traffic(filepath: str, out_dir: str, ip: str, columns:List[str], scale:List[float], signed:List[bool]):
    assert os.path.exists(input_file), 'invalid filepath: {}'.format(input_file)
    data = extract(filepath, nofile=True)
    frame = 0
    pc_data = None
    for f in data.frame:
        prev_frame = frame
        try:
            ip_src = f.info.ethernet.ipv4.src.exploded
            if ip_src != ip:
                continue
            payload = f.payload.payload.payload.payload.data
            frame, df_points = load_palicus_data(payload, columns, signed, scale)
            if prev_frame != frame:
                # store the previous frame
                filename = str(prev_frame).zfill(6) + '.csv'
                filepath = os.path.join(out_dir, filename)
                pc_data.to_csv(filepath, index=False)
                print('\t done with frame ', prev_frame)
                pc_data = None

            if pc_data is None:
                pc_data = df_points
            else:
                pc_data = pd.concat([pc_data, df_points])
        except Exception as e:
            print('[ERROR] ', str(e))

    # store the last frame
    filename = str(frame).zfill(6) + '.csv'
    filepath = os.path.join(out_dir, filename)
    pc_data.to_csv(filepath, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--pipeline', type=str, required=True)

    parser.add_argument('--input-dir', type=str, required=False, default='./data')
    parser.add_argument('--palicus-ip', type=str, required=False, default=PALICUS_IP)
    parser.add_argument('--n-frames', type=int, required=False, default=527)
    parser.add_argument('--reload', type=bool, required=False, default=False)

    args = parser.parse_args()
    pipeline = args.pipeline
    assert pipeline in ['bev', 'conversion', 'dm1', 'dm2', 'max', 'roi']

    if pipeline in ['conversion', 'roi']:
        cols = ['x', 'y', 'z']
        factor = [1/250, 1/250, 1/250]
        signed_ = [True, True, True]

    elif pipeline in ['dm1', 'dm2']:
        cols = ['px', 'py', 'radius']
        factor = [1, 1, 1/500]
        signed_ = [False, False, False]

    else:  # bev, max
        cols = ['px', 'py', 'z']
        factor = [1, 1, 1/250]
        signed_ = [False, False, True]

    input_file = os.path.join(args.input_dir, pipeline, 'latency', 'traffic_2.pcap')

    output_dir = os.path.join(args.input_dir, pipeline, 'precision', 'palicus')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if args.reload or len(os.listdir(output_dir)) != args.n_frames:
        print('parse data...')
        parse_palicus_traffic(input_file, output_dir, args.palicus_ip, columns=cols, scale=factor, signed=signed_)