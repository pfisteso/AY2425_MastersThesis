import os
import pandas as pd
import numpy as np
from pcapkit import extract
from typing import List, Tuple

# -- CSV --- #
def load_latency_data(pipeline: str = 'conversion', frame_min: int = 1, frame_max: int = 525) -> pd.DataFrame:
    filepath = os.path.join('./data', pipeline, 'latency', 'latency.csv')
    return _load_and_trim_pcap(filepath, frame_min, frame_max)


def load_frame_size_data(pipeline: str = 'conversion', throughput: int = 8,
                         frame_min: int = 1, frame_max: int = 525) -> pd.DataFrame:
    filepath = os.path.join('./data', pipeline, 'point_rate', 'frame_size_{}.csv'.format(throughput))
    return _load_and_trim_pcap(filepath, frame_min, frame_max)


def clean_latency_data(data: pd.DataFrame, col: str ='latency [ms]', factor: int = 2) -> pd.DataFrame:
    mean = data.mean()[col]
    std = data.std()[col]

    data = data.loc[data[col] >= mean - factor * std]
    data = data.loc[data[col] <= mean + factor * std]
    return data


def load_ground_truth(pipeline: str, frame_nr: int) -> pd.DataFrame:
    filename = str(frame_nr).zfill(6) + '.csv'
    filepath = os.path.join('./data', pipeline, 'precision', 'ground_truth', filename)
    assert os.path.exists(filepath), 'invalid filepath: {}'.format(filepath)

    return pd.read_csv(filepath)


def load_representation(pipeline: str, frame_nr: int, ground_truth: bool = False) -> pd.DataFrame:
    subdir = 'ground_truth' if ground_truth else 'palicus'
    filename = str(frame_nr).zfill(6) + '.csv'
    filepath = os.path.join('./data', pipeline, 'precision', subdir, filename)
    assert os.path.exists(filepath), 'invalid filepath: {}'.format(filepath)

    return pd.read_csv(filepath)

def load_precision_data(pipeline: str) -> pd.DataFrame:
    filepath = os.path.join('./data', pipeline, 'precision', 'precision.csv')
    assert os.path.exists(filepath), 'invalid file path: {}'.format(filepath)
    return pd.read_csv(filepath)


# -- PCAP --- #
def load_palicus_data(payload: bytes, columns:List[str], signed:List[bool], scale:List[float]) -> Tuple[int, pd.DataFrame]:
    frame_nr = int.from_bytes(payload[0:2], byteorder='big', signed=False)
    start = 2
    point_length = 2 * 3
    end = start + point_length
    points = []
    while end <= len(payload):
        f0 = int.from_bytes(payload[start:start + 2], byteorder='big', signed=signed[0]) * scale[0]
        f1 = int.from_bytes(payload[start + 2:start + 4], byteorder='big', signed=signed[1]) * scale[1]
        f2 = int.from_bytes(payload[start + 4:end], byteorder='big', signed=signed[2]) * scale[2]
        points.append([f0, f1, f2])
        start = end
        end = start + point_length
    result = pd.DataFrame(np.array(points), columns=columns)
    return frame_nr, result


def load_lidar_data(packet, prev_frame: int, prev_azimuth: int, delta_alpha:float) -> Tuple[int, float, pd.DataFrame]:
    payload = packet.payload.payload.payload.payload.data
    frame_nr = prev_frame
    points = []
    start = 2  # skip flag
    block_length = 2 + 2 * 3 * 16  # Azimuth (2B) + 2 Firing Sequences (16 Points x 3B)
    end = start + block_length
    azimuth = 0
    while end <= len(payload):
        # first firing sequence: read azimuth from file
        azimuth = int.from_bytes(payload[start:start + 2], "little", signed=False) / 100.0
        if azimuth < prev_azimuth:
            frame_nr += 1
        prev_azimuth = azimuth

        start += 2
        for i in range(16):
            point = payload[start + i * 3: start + (i + 1) * 3]
            radius = int.from_bytes(point[0:2], "little", signed=False) * 2 / 1000
            elevation = i if i % 2 == 1 else i - 15
            reflectance = int.from_bytes(point[2:3], "little", signed=False)

            points.append([frame_nr, radius, azimuth, elevation, reflectance])

        # second firing sequence: interpolate azimuth
        azimuth += delta_alpha
        azimuth = azimuth - 360.0 if azimuth > 360.0 else azimuth
        if azimuth < prev_azimuth:
            frame_nr += 1
        prev_azimuth = azimuth

        start += 3 * 16
        for i in range(16):
            point = payload[start + i * 3: start + (i + 1) * 3]
            radius = int.from_bytes(point[0:2], "little", signed=False) * 2 / 1000
            elevation = i if i % 2 == 1 else i - 15
            reflectance = int.from_bytes(point[2:3], "little", signed=False)

            points.append([frame_nr, radius, azimuth, elevation, reflectance])

        start += 3 * 16
        assert start == end
        start += 2  # skip flag
        end = start + block_length


    points = np.array(points)
    df_points = pd.DataFrame(points, columns=["frame_nr", "radius", "azimuth", "elevation", "reflectance"])
    return frame_nr, azimuth, df_points


def _load_and_trim_pcap(filepath, frame_min: int = 1, frame_max: int = 525) -> pd.DataFrame:
    assert os.path.exists(filepath), 'invalid file path: {}'.format(filepath)
    res = pd.read_csv(filepath)
    res = res.loc[res['frame_nr'] != frame_min - 1]
    res = res.loc[res['frame_nr'] != frame_max + 1]
    return res
