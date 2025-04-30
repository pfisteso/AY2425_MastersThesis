import os
import argparse
import pandas as pd

MIN_FRAME = 1
MAX_FRAME = 525

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-file", required=True)

    parser.add_argument("--min-frame", required=False, type=int, default=MIN_FRAME)
    parser.add_argument("--max-frame", required=False, type=int, default=MAX_FRAME)

    args = parser.parse_args()
    assert os.path.exists(args.input_dir), 'invalid input directory'

    results = []

    for file in os.listdir(args.input_dir):
        prefix = file.split('.')[0]
        if file.endswith('.csv') and len(prefix) == 6:
            frame_nr = int(prefix)
            if args.min_frame <= frame_nr <= args.max_frame:
                frame = pd.read_csv(os.path.join(args.input_dir, file))
                n_elements = len(frame)
                results.append([frame_nr, n_elements])

    df_res = pd.DataFrame(results, columns=['frame_nr', 'n_elements'])
    df_res.sort_values(by=['frame_nr'], inplace=True)
    df_res.to_csv(args.output_file, index=False)
