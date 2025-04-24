import os
import argparse
import pandas as pd
from utils import load_lidar_data, apply_conversion, apply_roi, apply_dm, apply_bev, apply_bev_count, apply_bev_mean_i
from utils.constants import LIDAR_IP
from pcapkit import extract

N_FRAMES = 527


def extract_lidar(filepath: str, ip: str, delta_alpha: float, res_dir: str):
    frame = 0
    azimuth = 0
    data = extract(filepath, nofile=True)
    pc_data = None
    for f in data.frame:
        prev_frame = frame
        try:
            ip_src = f.info.ethernet.ipv4.src.exploded
            if ip_src != ip:
                continue
            frame, azimuth, df_points = load_lidar_data(f, frame, azimuth, delta_alpha)
            if pc_data is None:
                pc_data = df_points
            else:
                pc_data = pd.concat([pc_data, df_points])
            if prev_frame != frame:
                # store the previous frame
                filename = str(prev_frame).zfill(6) + '.csv'
                filepath = os.path.join(res_dir, filename)
                prev_data = pc_data.loc[pc_data['frame_nr'] == prev_frame]
                prev_data.to_csv(filepath, index=False)
                print('\t done with frame ', prev_frame)
                pc_data = pc_data.loc[pc_data['frame_nr'] == frame]
        except Exception as e:
            print('[ERROR] ', str(e))

    # store the last frame
    filename = str(frame).zfill(6) + '.csv'
    filepath = os.path.join(res_dir, filename)
    pc_data.to_csv(filepath, index=False)


def build_representation(input_dir: str, output_dir: str, pipeline: str, reload: bool):
    assert os.path.exists(input_dir)
    assert os.path.exists(output_dir)
    assert pipeline in ['bev', 'conversion', 'dm1', 'dm2', 'max', 'roi', 'bev_mean_i', 'bev_count']

    for file in os.listdir(input_dir):
        output_file = os.path.join(output_dir, file)
        # skip already processed frames
        if not reload and os.path.exists(output_file):
            continue

        pc = pd.read_csv(os.path.join(input_dir, file))
        if pipeline == 'conversion':
            gt = apply_conversion(pc)
        elif pipeline == 'roi':
            gt = apply_roi(pc)
        elif pipeline == 'dm1':
            gt = apply_dm(pc, pipeline=1, delta_alpha=args.delta_phi)
        elif pipeline == 'dm2':
            gt = apply_dm(pc, pipeline=2, delta_alpha=args.delta_phi)
        elif pipeline == 'bev_count':
            gt = apply_bev_count(pc)
        elif pipeline == 'bev_mean_i':
            gt = apply_bev_mean_i(pc)
        else:  # bev, max
            gt = apply_bev(pc)

        gt.to_csv(output_file, index=False)
        print('\t done with frame', file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--pipeline', required=True)

    parser.add_argument('--n-frames', required=False, default=N_FRAMES)
    parser.add_argument('--ground-truth-file', required=False, default='./data/VLP16_traffic.pcap')
    parser.add_argument('--data-dir', required=False, default='./data')
    parser.add_argument('--delta-phi', required=False, type=float, default=0.1)
    parser.add_argument('--lidar-ip', required=False, default=LIDAR_IP)
    parser.add_argument('--reload', required=False, type=bool, default=False)

    args = parser.parse_args()

    pc_dir= os.path.join(args.data_dir, 'z_point_clouds', 'ground_truth')
    if not os.path.exists(pc_dir):
        os.makedirs(pc_dir)

    lidar_file = args.ground_truth_file
    if args.reload or len(os.listdir(pc_dir)) != args.n_frames:
        assert os.path.exists(lidar_file), 'invalid data path: {}'.format(lidar_file)
        print('Extract LiDAR data ...')
        extract_lidar(lidar_file, args.lidar_ip, args.delta_phi, res_dir=pc_dir)
        print('... done')

    pipeline = args.pipeline

    experiments_path = os.path.join(args.data_dir, pipeline, 'precision')
    out_dir = os.path.join(experiments_path, 'ground_truth')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if args.reload or len(os.listdir(out_dir)) != args.n_frames:
        print('Build target representation...')
        build_representation(input_dir=pc_dir, output_dir=out_dir, pipeline=pipeline, reload=args.reload)
        print('... done')






