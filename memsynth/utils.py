import os
import logging.config

import yaml

import coloredlogs

def setup_logging(
    default_path='logging.yaml',
    default_level=logging.INFO,
    env_key='LOG_LOC',
    level_styles=None
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    if level_styles:
        os.environ['COLOREDLOGS_LEVEL_STYLES'] = level_styles
    else:
        os.environ['COLOREDLOGS_LEVEL_STYLES'] = 'spam=22;debug=28;' \
                                                 'verbose=34;notice=220;' \
                                                 'warning=202;success=118,' \
                                                 'bold;error=124;' \
                                                 'critical=background=red'

    coloredlogs.install(level=default_level)
