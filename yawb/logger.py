
import os
import logging

logger = logging.getLogger("yawb")

def init_log(verbosity=0):

    if verbosity == 1:
        level = logging.INFO
    elif verbosity > 1:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=logging.ERROR,
        format="yawb:%(levelname)s:%(message)s"
    )
    logger.level = level
