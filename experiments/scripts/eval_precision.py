import os
import math
import argparse
import pandas as pd


def eval_precision_point_cloud(ground_truth: str, palicus: str, out_path: str):
    global_result = []
    excluded_frames = []
    intermediate_dir = os.path.join(os.path.dirname(out_path), 'compare')
    if not os.path.exists(intermediate_dir):
        os.makedirs(intermediate_dir)

    for file in os.listdir(ground_truth):
        assert file in os.listdir(palicus), 'invalid file: {}'.format(file)
        frame = int(file.split('.')[0])

        gt_file = os.path.join(ground_truth, file)
        palicus_file = os.path.join(palicus, file)

        assert os.path.exists(gt_file), 'invalid file: {}'.format(gt_file)
        assert os.path.exists(palicus_file), 'invalid file: {}'.format(palicus_file)

        gt = pd.read_csv(gt_file).loc[:, ['x', 'y', 'z']]
        pal = pd.read_csv(palicus_file)
        pal.rename(columns={'x': 'x_pal', 'y': 'y_pal', 'z': 'z_pal'}, inplace=True)

        if len(gt) != len(pal):
            print('skip frame ', frame)
            excluded_frames.append([frame, len(gt), len(pal)])
            continue
        df_compare = pd.concat([gt, pal], axis=1)
        df_compare['diff'] = df_compare.apply(lambda row:
                                              math.sqrt((row['x'] - row['x_pal']) ** 2 +
                                                        (row['y'] - row['y_pal']) ** 2 +
                                                        (row['z'] - row['z_pal']) ** 2), axis=1)

        df_compare.to_csv(os.path.join(intermediate_dir, file),
                          index=False)

        min_ = df_compare.min()['diff']
        max_ = df_compare.max()['diff']
        mean_error = df_compare.mean()['diff']

        global_result.append([frame, mean_error, min_, max_])
        print('\tdone with frame ', frame)

    df_result = pd.DataFrame(global_result, columns=['frame', 'mean error', 'min', 'max'])
    df_result.to_csv(out_path, index=False)

    df_excluded = pd.DataFrame(excluded_frames, columns=['frame', 'GT', 'Palicus'])
    df_excluded.to_csv(os.path.join(os.path.dirname(out_path), 'excluded_frames.csv'), index=False)


def eval_precision_dm(ground_truth: str, palicus: str, out_path: str):
    global_result = []
    excluded_frames = []
    intermediate_dir = os.path.join(os.path.dirname(out_path), 'compare')
    if not os.path.exists(intermediate_dir):
        os.makedirs(intermediate_dir)

    for file in os.listdir(ground_truth):
        assert file in os.listdir(palicus), 'invalid file: {}'.format(file)
        frame = int(file.split('.')[0])

        gt_file = os.path.join(ground_truth, file)
        palicus_file = os.path.join(palicus, file)

        assert os.path.exists(gt_file), 'invalid file: {}'.format(gt_file)
        assert os.path.exists(palicus_file), 'invalid file: {}'.format(palicus_file)

        gt = pd.read_csv(gt_file).loc[:, ['px', 'py', 'radius']]
        pal = pd.read_csv(palicus_file)
        pal.rename(columns={'px': 'px_pal', 'py': 'py_pal'}, inplace=True)

        if len(gt) != len(pal):
            print('skip frame ', frame)
            excluded_frames.append([frame, len(gt), len(pal)])
            continue
        df_compare = pd.concat([gt, pal], axis=1)
        df_compare['diff'] = df_compare.apply(lambda row: abs(row['px'] - row['px_pal']) + abs(row['py'] - row['py_pal']), axis=1)

        df_compare.to_csv(os.path.join(intermediate_dir, file), index=False)
        wrong_pixels = df_compare.loc[df_compare['diff'] > 0]

        global_result.append([frame, len(wrong_pixels), round(len(wrong_pixels) / len(df_compare) * 100.0, 2)])
        print('\tdone with frame ', frame)

    df_result = pd.DataFrame(global_result, columns=['frame', '# FALSE', '% FALSE'])
    df_result.to_csv(out_path, index=False)

    df_excluded = pd.DataFrame(excluded_frames, columns=['frame', 'GT', 'Palicus'])
    df_excluded.to_csv(os.path.join(os.path.dirname(out_path), 'excluded_frames.csv'), index=False)


def eval_precision_bev(ground_truth: str, palicus: str, out_path: str, ftr: str):
    global_result = []
    intermediate_dir = os.path.join(os.path.dirname(out_path), 'compare')
    if not os.path.exists(intermediate_dir):
        os.makedirs(intermediate_dir)

    for file in os.listdir(ground_truth):
        assert file in os.listdir(palicus), 'invalid file: {}'.format(file)
        frame = int(file.split('.')[0])

        gt_image = pd.read_csv(os.path.join(ground_truth, file)).loc[:, ['px', 'py', ftr]]
        gt_image.rename(columns={ftr: 'GT'}, inplace=True)

        pal_image = pd.read_csv(os.path.join(palicus, file))
        pal_image.rename(columns={ftr: 'PAL'}, inplace=True)

        df_compare = pd.merge(gt_image, pal_image, how='outer', on=['px', 'py'])
        df_compare['diff'] = df_compare.apply(lambda row: abs(row['GT']) if pd.isna(row['PAL']) else
                                                          abs(row['PAL']) if pd.isna(row['GT']) else
                                                          abs(row['GT'] - row['PAL']), axis=1)

        df_compare.to_csv(os.path.join(intermediate_dir, file),
                          index=False)

        min_ = df_compare.min()['diff']
        max_ = df_compare.max()['diff']
        mean_error = df_compare.mean()['diff']

        global_result.append([frame, mean_error, min_, max_])
        print('\tdone with frame ', frame)

    df_result = pd.DataFrame(global_result, columns=['frame', 'mean error', 'min', 'max'])
    df_result.to_csv(out_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--pipeline', required=True)

    parser.add_argument('--data-dir', required=False, default='./data')

    args = parser.parse_args()

    assert args.pipeline in ['bev', 'bev_mean', 'conversion', 'dm1', 'dm2', 'roi']

    gt_dir = os.path.join(args.data_dir, args.pipeline, 'precision', 'ground_truth')
    palicus_dir = os.path.join(args.data_dir, args.pipeline, 'precision', 'palicus')

    assert os.path.exists(gt_dir)
    assert os.path.exists(palicus_dir)
    assert len(os.listdir(gt_dir)) == len(os.listdir(palicus_dir))

    output_path = os.path.join(args.data_dir, args.pipeline, 'precision', 'precision.csv')

    if args.pipeline in ['bev', 'bev_mean']:
        f = 'z' if args.pipeline == 'bev' else 'i'
        eval_precision_bev(gt_dir, palicus_dir, output_path, f)
    elif args.pipeline in ['dm1', 'dm2']:
        eval_precision_dm(gt_dir, palicus_dir, output_path)
    else:
        eval_precision_point_cloud(gt_dir, palicus_dir, output_path)
