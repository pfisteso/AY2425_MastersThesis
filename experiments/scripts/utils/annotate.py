import numpy as np
import pandas as pd
from pcapkit import *



def annotate_lidar_packet(packet, pkt_nr: int, curr_frame_nr:int, delta_phi:float, prev_azimuth:float):
    timestamp = packet.info.time
    payload = packet.payload.payload.payload.payload.data
    frame_nr = curr_frame_nr
    package_frame = []
    azimuth = 0

    start = 2  # skip flag
    block_length = 2 + 2 * 3 * 16  # Azimuth (2B) + 2 Firing Sequences (16 Points x 3B)
    end = start + block_length
    while end <= len(payload):
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