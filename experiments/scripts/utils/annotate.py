import numpy as np
import pandas as pd
from pcapkit import extract

def annotate_lidar_pcap(file_path: str, output_path: str, delta_alpha:float):
    data = extract(file_path, nofile=True)
    package_frame = []
    prev_azimuth = 0
    frame_nr = 0
    package_nr = 0
    for f in data.frame:
        package_nr += 1
        timestamp = f.timestamp
        print(timestamp)
        payload = f.payload.payload.payload.payload.data

        start = 2  # skip flag
        block_length = 2 + 2 * 3 * 16  # Azimuth (2B) + 2 Firing Sequences (16 Points x 3B)
        end = start + block_length
        while end <= len(payload):
            # first firing sequence: read azimuth from file
            azimuth = int.from_bytes(payload[start:start + 2], "little", signed=False) / 100.0
            if azimuth < prev_azimuth:
                if start > 2:
                    package_frame.append([package_nr, timestamp, frame_nr])
                frame_nr += 1

            prev_azimuth = azimuth
            # second firing sequence: interpolate azimuth
            azimuth += delta_alpha
            azimuth = azimuth - 360.0 if azimuth > 360.0 else azimuth
            if azimuth < prev_azimuth:
                if start > 2:
                    package_frame.append([package_nr, timestamp, frame_nr])
                frame_nr += 1
            prev_azimuth = azimuth

            package_frame.append([package_nr, timestamp, frame_nr])

            start += block_length
            assert start == end
            start += 2  # skip flag
            end = start + block_length

    log = pd.DataFrame(np.array(package_frame), columns=['package_nr', 'timestamp', 'frame_nr'])
    log.drop_duplicates(inplace=True)
    log.to_csv(output_path, index=False)
