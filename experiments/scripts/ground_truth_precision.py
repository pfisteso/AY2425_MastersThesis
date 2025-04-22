import os
import argparse
import pandas as pd
from utils import load_lidar_data, apply_conversion, apply_roi, apply_dm, apply_bev
from utils.constants import LIDAR_IP
from pcapkit import extract



def extract_lidar(filepath: str, ip: str, delta_alpha: float) -> pd.DataFrame:
    frame = 0
    azimuth = 0
    data = extract(filepath, nofile=True)
    pc_data = None
    for f in data.frame:
        try:
            ip_src = f.info.ethernet.ipv4.src.exploded
            if ip_src != ip:
                continue
            frame, azimuth, df_points = load_lidar_data(f, frame, azimuth, delta_alpha)
            if pc_data is None:
                pc_data = df_points
            else:
                pc_data = pd.concat([pc_data, df_points])
        except Exception as e:
            print('[ERROR] ', str(e))
    return pc_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--pipeline', required=True)

    parser.add_argument('--ground-truth-file', required=False, default='./data/VLP16_traffic.pcap')
    parser.add_argument('--data-dir', required=False, default='./data')
    parser.add_argument('--delta-phi', required=False, type=float, default=0.1)
    parser.add_argument('--lidar-ip', required=False, default=LIDAR_IP)
    parser.add_argument('--reload', required=False, type=bool, default=False)


    args = parser.parse_args()

    gt_path = os.path.join(args.data_dir, 'ground_truth.csv')
    lidar_file = args.ground_truth_file
    if args.reload or not os.path.exists(gt_path):
        assert os.path.exists(lidar_file), 'invalid data path: {}'.format(lidar_file)
        print('Extract LiDAR data ...')
        gt_point_cloud = extract_lidar(lidar_file, args.lidar_ip, args.delta_phi)
        gt_point_cloud.to_csv(gt_path, index=False)
        print('... done')
    else:
        gt_point_cloud = pd.read_csv(gt_path)

    pipeline = args.pipeline
    assert pipeline in ['bev', 'conversion', 'dm1', 'dm2', 'max', 'roi']

    experiments_path = os.path.join(args.data_dir, pipeline, 'precision')
    if not os.path.exists(experiments_path):
        os.makedirs(experiments_path)
    gt_path = os.path.join(experiments_path, 'ground_truth.csv')
    if args.reload or not os.path.exists(gt_path):
        print('Build target representation...')
        if pipeline == 'conversion':
            gt = apply_conversion(gt_point_cloud)
        if pipeline == 'roi':
            gt = apply_roi(gt_point_cloud)
        if pipeline == 'dm1':
            gt = apply_dm(gt_point_cloud, pipeline=1, delta_alpha=args.delta_phi)
        if pipeline == 'dm2':
            gt = apply_dm(gt_point_cloud, pipeline=2, delta_alpha=args.delta_phi)
        else:  # bev, max
            gt = apply_bev(gt_point_cloud)

        gt.to_csv(gt_path, index=False)
        print('\tdone')






