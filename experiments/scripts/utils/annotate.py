import numpy as np
import pandas as pd
from typing import Tuple, List


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


def extract_palicus_data(packet, extract_frame: int, columns: List[str], scale: List[float], signed: List[bool]) -> Tuple[bool, bool, pd.DataFrame]:
    payload = packet.payload.payload.payload.payload.data
    frame_nr = int.from_bytes(payload[0:2], byteorder='big', signed=False)

    result = None
    valid = frame_nr == extract_frame
    continue_ = frame_nr <= extract_frame

    if valid:
        start = 2
        point_length = 2 * 3
        end = start + point_length
        points = []
        while end <= len(payload):
            f0 = int.from_bytes(payload[start:start+2], byteorder='big', signed=signed[0]) * scale[0]
            f1 = int.from_bytes(payload[start+2:start+4], byteorder='big', signed=signed[1]) * scale[1]
            f2 = int.from_bytes(payload[start+4:end], byteorder='big', signed=signed[2]) * scale[2]
            points.append([f0, f1, f2])
            start = end
            end = start + point_length
        result = pd.DataFrame(np.array(points), columns=columns)
        if (f0 == 0 and f1 == 0 and f2 == 0):
            print('all zero element')

    return valid, continue_, result

def extract_lidar_data(packet, extract_frame: int, prev_frame: int, prev_azimuth: int) -> pd.DataFrame:
    pass