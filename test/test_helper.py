import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
autonose_root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
