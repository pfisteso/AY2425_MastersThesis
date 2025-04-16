import os
import pandas as pd


def load_latency_data(pipeline: str = 'conversion', frame_min: int = 1, frame_max: int = 525) -> pd.DataFrame:
    filepath = os.path.join('./data', pipeline, 'latency', 'latency.csv')
    return _load_and_trim_pcap(filepath, frame_min, frame_max)


def load_frame_size_data(pipeline: str = 'conversion', experiment: str ='point_rate',
                         frame_min: int = 1, frame_max: int = 525) -> pd.DataFrame:
    filepath = os.path.join('./data', pipeline, experiment, 'frame_size.csv')
    return _load_and_trim_pcap(filepath, frame_min, frame_max)


def clean_latency_data(data: pd.DataFrame, col: str ='latency [ms]', factor: int = 2) -> pd.DataFrame:
    mean = data.mean()[col]
    std = data.std()[col]

    data = data.loc[data[col] >= mean - factor * std]
    data = data.loc[data[col] <= mean + factor * std]
    return data


def _load_and_trim_pcap(filepath, frame_min: int = 1, frame_max: int = 525) -> pd.DataFrame:
    assert os.path.exists(filepath), 'invalid file path: {}'.format(filepath)
    res = pd.read_csv(filepath)
    res = res.loc[res['frame_nr'] != frame_min - 1]
    res = res.loc[res['frame_nr'] != frame_max + 1]
    return res
