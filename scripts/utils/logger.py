import os
import sys
import re
import logging
from logging.handlers import RotatingFileHandler

from config import Config

cf = Config.get_instance()


class Logger():
    _logger = None

    @classmethod
    def get_logger(cls):
        filename = re.sub(r'\.py$', '', os.path.basename(sys.argv[0]))

        if cls._logger is None:
            logger = logging.getLogger('root')
            logger.setLevel(getattr(logging, cf.env.LOG_LEVEL.upper()))

            fh = RotatingFileHandler(
                filename='logs/{}.log'.format(filename),
                maxBytes=(cf.env.LOG_ROTATE_MAX_MB * 1024 * 1024),
                backupCount=cf.env.LOG_ROTATE_BACKUP_COUNT)
            fh.setLevel(logging.DEBUG)

            fmt = logging.Formatter(
                fmt=cf.LOG_FILE_FORMAT,
                datefmt=cf.LOG_DATE_FORMAT)

            fh.setFormatter(fmt)
            logger.addHandler(fh)

            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)

            fmt = logging.Formatter(
                fmt=cf.LOG_CONSOLE_FORMAT,
                datefmt=cf.LOG_DATE_FORMAT)

            ch.setFormatter(fmt)
            logger.addHandler(ch)

            cls._logger = logger
        return cls._logger

