import math
import numpy as np
import pandas as pd


def annotate_lidar_packet(packet, pkt_nr: int, curr_frame_nr: int, delta_phi: float, prev_azimuth: float):
    timestamp = packet.info.time
    payload = packet.payload.payload.payload.payload.data
    frame_nr = curr_frame_nr
    package_frame = []
    azimuth = 0

    start = 2  # skip flag
    block_length = 2 + 2 * 3 * 16  # Azimuth (2B) + 2 Firing Sequences (16 Points x 3B)
    end = start + block_length
    while end <= len(payload):
        assert payload[start - 2:start].hex() == 'ffee'  # start after the flag marking the next data block
        # first firing sequence: read azimuth from file
        azimuth = int.from_bytes(payload[start:start + 2], "little", signed=False) / 100.0
        if azimuth < prev_azimuth:
            if start > 2:
                package_frame.append([pkt_nr, timestamp, frame_nr])
            frame_nr += 1

        prev_azimuth = azimuth
        # second firing sequence: interpolate azimuth
        azimuth += delta_phi
        azimuth = azimuth - 360.0 if azimuth > 360.0 else azimuth
        if azimuth < prev_azimuth:
            if start > 2:
                package_frame.append([pkt_nr, timestamp, frame_nr])
            frame_nr += 1
        prev_azimuth = azimuth

        package_frame.append([pkt_nr, timestamp, frame_nr])

        start += block_length
        assert start == end
        start += 2  # skip flag
        end = start + block_length

    log = pd.DataFrame(np.array(package_frame), columns=['pkt_nr', 'timestamp', 'frame_nr'])
    log.drop_duplicates(inplace=True)
    return log, frame_nr, azimuth


def annotate_palicus_packet(packet, pkt_nr: int):
    timestamp = packet.info.time
    payload = packet.payload.payload.payload.payload.data
    frame_nr = int.from_bytes(payload[0:2], byteorder='big', signed=False)

    return pd.DataFrame(np.array([[pkt_nr, timestamp, frame_nr]]), columns=['pkt_nr', 'timestamp', 'frame_nr'])


def apply_conversion(point_cloud: pd.DataFrame) -> pd.DataFrame:
    point_cloud['x'] = point_cloud.apply(lambda row: row['radius'] * math.cos(math.radians(row['elevation'])) * math.sin(math.radians(row['azimuth'])), axis=1)
    point_cloud['y'] = point_cloud.apply(lambda row: row['radius'] * math.cos(math.radians(row['elevation'])) * math.cos(math.radians(row['azimuth'])), axis=1)
    point_cloud['z'] = point_cloud.apply(lambda row: row['radius'] * math.sin(math.radians(row['elevation'])), axis=1)
    return point_cloud


def apply_roi(point_cloud: pd.DataFrame) -> pd.DataFrame:
    point_cloud = point_cloud.loc[point_cloud['radius'] > 0]
    point_cloud = apply_conversion(point_cloud)
    return point_cloud


def apply_dm(point_cloud: pd.DataFrame, pipeline: int, delta_alpha: float) -> pd.DataFrame:
    assert pipeline in [1, 2]
    point_cloud = apply_roi(point_cloud)
    point_cloud['px'] = point_cloud.apply(lambda row: math.floor(row['azimuth'] / delta_alpha), axis=1)
    if pipeline == 1:
        point_cloud['py'] = point_cloud.apply(lambda row: math.floor(row['elevation'] / 2), axis=1)
    else:  # pipeline == 2
        point_cloud['py'] = point_cloud.apply(lambda row: math.floor((row['elevation'] + 15) / 2), axis=1)

    return point_cloud


def apply_bev(point_cloud: pd.DataFrame) -> pd.DataFrame:
    point_cloud = _annotate_bev(point_cloud)

    bev = point_cloud.groupby(['frame_nr', 'px', 'py']).max()['z']
    bev = bev.reset_index(drop=False)
    return bev

def apply_bev_mean_i(point_cloud: pd.DataFrame) -> pd.DataFrame:
    point_cloud = _annotate_bev(point_cloud)
    point_cloud = point_cloud.rename(columns={'reflectance': 'i'})
    bev = point_cloud.groupby(['frame_nr', 'px', 'py']).mean()['i']
    bev = bev.reset_index(drop=False)
    return bev

def apply_bev_count(point_cloud: pd.DataFrame) -> pd.DataFrame:
    point_cloud = _annotate_bev(point_cloud)
    bev = point_cloud.groupby(['frame_nr', 'px', 'py']).count()['z']
    bev = bev.reset_index(drop=False)
    return bev


def _annotate_bev(point_cloud: pd.DataFrame) -> pd.DataFrame:
    point_cloud = apply_roi(point_cloud)
    point_cloud = point_cloud.loc[point_cloud['x'] >= -3]
    point_cloud = point_cloud.loc[point_cloud['x'] <= 3]
    point_cloud = point_cloud.loc[point_cloud['y'] >= -3]
    point_cloud = point_cloud.loc[point_cloud['y'] <= 3]
    point_cloud['px'] = point_cloud.apply(lambda row: math.floor((row['x'] + 3) / 0.2), axis=1)
    point_cloud['py'] = point_cloud.apply(lambda row: math.floor((row['y'] + 3) / 0.2), axis=1)

    return point_cloud