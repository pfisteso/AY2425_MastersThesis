import argparse
import os
import json
from jsonschema import validate

from utils.scheme import palicus_config_scheme
from utils import transmit_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', metavar='config_file', required=True,
                        help='path to the configuration file')

    args = parser.parse_args()
    config_file = args.config_file
    assert os.path.exists(config_file) and os.path.isfile(config_file) and config_file.endswith('.json'), 'invalid file path: {}'.format(config_file)
    config = json.load(open(config_file))
    validate(instance=config, schema=palicus_config_scheme)

    transmit_config(config)


