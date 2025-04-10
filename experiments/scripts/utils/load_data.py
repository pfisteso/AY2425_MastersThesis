import os
import pandas as pd


def load_latency_data(throughput: str = '8Mbps', pipeline: str = 'conversion', max_frame: int = 525) -> pd.DataFrame:
    filepath = os.path.join('./data', pipeline, throughput, 'latency.csv')
    assert os.path.exists(filepath), 'invalid file path: {}'.format(filepath)
    res = pd.read_csv(filepath)
    res = res.loc[res['frame_nr'] > 0]
    res = res.loc[res['frame_nr'] <= max_frame]
    return res


def load_packet_data(throughput: str = '8Mbps', pipeline: str = 'conversion', max_frame: int = 525) -> pd.DataFrame:
    filepath = os.path.join('./data', pipeline, throughput, 'palicus.csv')
    assert os.path.exists(filepath), 'invalid file path: {}'.format(filepath)
    res = pd.read_csv(filepath)
    res = res.loc[res['frame_nr'] > 0]
    res = res.loc[res['frame_nr'] <= max_frame]
    return res


def clean_latency_data(data: pd.DataFrame, col: str ='latency [ms]', factor: int = 2) -> pd.DataFrame:
    mean = data.mean()[col]
    std = data.std()[col]

    data = data.loc[data[col] >= mean - factor * std]
    data = data.loc[data[col] <= mean + factor * std]
    return data