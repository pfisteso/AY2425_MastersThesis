import socket

from .constants import PALICUS_IP, CONFIG_PORT, I_FACE
from .data_models import PalicusConfiguration

def transmit_config(config: dict, iface=I_FACE, ip=PALICUS_IP, port=CONFIG_PORT):
    config_model = PalicusConfiguration(**config)
    msg = config_model.get_config_bytes()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, str(iface + '\0').encode('utf-8'))
    s.sendto(msg, (ip, port))
    s.close()
