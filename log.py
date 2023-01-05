import json
import pathlib
import logging.config

# Setup logging from the log.json config file.
# This makes it easy to change logging level, output to a file, etc.
logging.config.dictConfig(json.loads(pathlib.Path(__file__).parent.joinpath('log.json').read_text()))
log = logging.getLogger('logger')