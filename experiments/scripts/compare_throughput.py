import os
import sys
import argparse
import numpy as np
import pandas as pd

from typing import List


def compare_images(gt: pd.DataFrame, frame: pd.DataFrame, throughput: int, ftr: List[str]):
    assert len(ftr) == 3
    delta = len(frame) - len(gt)
    assert delta <= 0
    if delta != 0:
        print('frame size mismatch for t = {}: '.format(throughput), len(gt), ' - ' , len(frame))

    delta_elements = []
    off = 0
    for i in range(max(len(gt), len(frame))):
        px = gt.loc[i, 'px']
        py = gt.loc[i, 'py']
        color = gt.loc[i, ftr[2]]

        df_frame = frame.loc[frame['px'] == px]
        df_frame = df_frame.loc[df_frame['py'] == py]
        if len(df_frame) == 0:
            delta_elements.append([px, py, color, None])
            continue
        else:
            found = False
            value = 0
            delta = sys.float_info.max
            for pixel in df_frame.itertuples():
                if pixel.z == color:
                    found = True
                    break
                else:
                    diff = abs(pixel.z - color)
                    if diff < delta:
                        value = pixel.z
                        delta = diff
            if not found:
                delta_elements.append([px, py, color, value])

    return pd.DataFrame(delta_elements, columns=['px', 'py', 'gt', 'nearest'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--pipeline", required=True)
    # parser.add_argument("--frame-nr", type=int, required=True)

    parser.add_argument("--data-dir", default='./data')

    args = parser.parse_args()

    pipeline = args.pipeline
    # frame_nr = args.frame_nr
    for frame_nr in range(1, 526):
        frame_file_name = str(frame_nr).zfill(6) + '.csv'

        input_dir = os.path.join(args.data_dir, pipeline, 'throughput')
        assert os.path.exists(input_dir)

        for t in [8, 16, 32, 64, 128]:
            t_dir = os.path.join(input_dir, 'palicus_{}'.format(t))
            assert os.path.exists(t_dir), 'path {} does not exist'.format(t_dir)
            file_path = os.path.join(t_dir, frame_file_name)
            assert os.path.exists(file_path), 'path {} does not exist'.format(file_path)

        df_8 = pd.read_csv(os.path.join(input_dir, 'palicus_8', frame_file_name))
        df_16 = pd.read_csv(os.path.join(input_dir, 'palicus_16', frame_file_name))
        df_32 = pd.read_csv(os.path.join(input_dir, 'palicus_32', frame_file_name))
        df_64 = pd.read_csv(os.path.join(input_dir, 'palicus_64', frame_file_name))
        df_128 = pd.read_csv(os.path.join(input_dir, 'palicus_128', frame_file_name))

        if 'dm' in pipeline:
            ftr = ['px', 'py', 'radius']
        elif pipeline == 'bev':
            ftr = ['px', 'py', 'z']
        else:
            ftr = ['x', 'y', 'z']

        out_dir = os.path.join(input_dir, 'compare', frame_file_name.split('.')[0])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if pipeline in ['dm1', 'dm2', 'bev']:
            compare_8_16 = compare_images(df_8, df_16, 16, ftr)
            compare_8_32 = compare_images(df_8, df_32, 32, ftr)
            compare_8_64 = compare_images(df_8, df_64, 64, ftr)
            compare_8_128 = compare_images(df_8, df_128, 128, ftr)
            # save
            if len(compare_8_16) > 0:
                compare_8_16.to_csv(os.path.join(out_dir, 'compare_8_16.csv'), index=False)
            if len(compare_8_32) > 0:
                compare_8_32.to_csv(os.path.join(out_dir, 'compare_8_32.csv'),index=False)
            if len(compare_8_64) > 0:
                compare_8_64.to_csv(os.path.join(out_dir, 'compare_8_64.csv'), index=False)
            if len(compare_8_128) > 0:
                compare_8_128.to_csv(os.path.join(out_dir, 'compare_8_128.csv'), index=False)
        if len(os.listdir(out_dir)) == 0:
            os.rmdir(out_dir)

