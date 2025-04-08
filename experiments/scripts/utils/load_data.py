import os
import pandas as pd


def load_latency_data(throughput: str = '8Mbps', pipeline: str = 'conversion', max_frame: int = 525) -> pd.DataFrame:
    filepath = os.path.join('./data', throughput, pipeline, 'latency.csv')
    assert os.path.exists(filepath)
    res = pd.read_csv(filepath)
    res = res.loc[res['frame_nr'] > 0]
    res = res.loc[res['frame_nr'] <= max_frame]
    return res
