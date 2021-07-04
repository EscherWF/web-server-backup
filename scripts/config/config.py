import os
import re
from collections import namedtuple


class Config():

    APP_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PROJECT_PATH = os.path.abspath(os.path.dirname(APP_PATH))
    LOGS_PATH = '{}/logs'.format(PROJECT_PATH)

    # NOTE: ホストが増えたらここも増やす
    HOST_NAMES = [
        'example-host1',
        # 'example-host2'
    ]

    SFTP_EXCLUDE_DIR = 'data'

    NAS_RETRY_COUNT = 5
    NAS_DIR_FORMAT = '%Y%m%d'
    NAS_MOUNTED_POINT = 'mnt'

    # Logging
    LOG_FILE_FORMAT = '[%(asctime)s][%(levelname)s][%(module)s:%(lineno)d] %(message)s'
    LOG_CONSOLE_FORMAT = '[%(asctime)s][%(levelname)s][%(module)s:%(lineno)d] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._init_env()

    def _init_env(self):
        env_path = '{}/.env'.format(self.PROJECT_PATH)

        env = {}
        with open(env_path, 'r') as fp:
            lines = fp.read().strip()
            for line in lines.split('\n'):
                if line.strip()[0:1] == '#':
                    continue
                kv = [kv.strip() for kv in line.split('=')]
                if len(kv) == 2:
                    v = kv[1]
                    if v == 'null':
                        v = None
                    elif v.lower() == 'true':
                        v = True
                    elif v.lower() == 'false':
                        v = False
                    elif re.match('[1-9][0-9]*$', v):
                        v = int(v)
                    elif re.match('.*,+.*$', v):
                        v = [vi.strip() for vi in v.split(',')]
                    env[kv[0]] = v
        self.env = namedtuple('Env', env.keys())(*env.values())
