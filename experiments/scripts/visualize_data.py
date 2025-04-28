import os
import argparse
import pandas as pd

from utils import visualize2d, visualize3d

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input-file', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--pipeline', required=True)

    args = parser.parse_args()

    pipeline = args.pipeline
    assert pipeline in ['bev', 'conversion', 'dm1', 'dm2', 'max', 'roi']
    dimensionality = 3 if pipeline in ['conversion', 'roi'] else 3

    assert os.path.exists(args.input_file) and args.input_file.endswith('.csv'), 'invalid input file: {}'.format(args.input_file)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    filename = args.input_file.split('/')[-1]  # retrive the filename
    filename = filename.split('.')[0] + '.png' # replace csv -> png
    output_file = os.path.join(args.output_dir, filename)

    data = pd.read_csv(args.input_file)
    if pipeline in ['dm1', 'dm2']:
        data = data.rename(columns={'radius': 'color'})
    if pipeline in ['bev', 'max']:
        data = data.rename(columns={'z': 'color'})


    if dimensionality == 2:
        img = visualize2d(data, flip_img=('dm' in pipeline))
    else:
        img = visualize3d(data)

    img.save(output_file)
