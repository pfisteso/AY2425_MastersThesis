import os
import argparse
import pandas as pd

from utils import visualize2d, visualize3d

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input-file', required=True)
    parser.add_argument('--output-file', required=True)
    parser.add_argument('--pipeline', required=True)
    parser.add_argument('--color-min', required=False, type=float, default=0.0)
    parser.add_argument('--color-max', required=False, type=float, default=255.0)

    args = parser.parse_args()

    pipeline = args.pipeline
    assert pipeline in ['bev', 'conversion', 'dm1', 'dm2', 'roi']
    dimensionality = 3 if pipeline in ['conversion', 'roi'] else 2

    assert os.path.exists(args.input_file) and args.input_file.endswith('.csv'), 'invalid input file: {}'.format(args.input_file)
    output_dir = os.path.dirname(args.output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    data = pd.read_csv(args.input_file)
    if pipeline in ['dm1', 'dm2']:
        data = data.rename(columns={'radius': 'color'})
    if pipeline == 'bev':
        data = data.rename(columns={'z': 'color'})

    if dimensionality == 2:
        img = visualize2d(data, args.color_min, args.color_max - args.color_min, flip_img=('dm' in pipeline))
    else:
        img = visualize3d(data)

    img.save(args.output_file)
