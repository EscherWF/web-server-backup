import subprocess

from config import Config
from utils import Logger

cf = Config.get_instance()
lg = Logger.get_logger()


class TimeoutExpired(Exception):
    pass


class Mount():
    CMD_TIMEOUT = 20

    def __init__(self):
        pass

    def mount(self):
        try:
            subprocess.run(
                [
                    'mount',
                    '-t', 'nfs',
                    '{}:/{}'.format(cf.env.NAS_HOST, cf.env.NAS_SHARED_DIR),
                    '/{}'.format(cf.NAS_MOUNTED_POINT),
                    '-o', 'nolock'
                ], timeout=self.CMD_TIMEOUT)
        except subprocess.TimeoutExpired as e:
            raise TimeoutExpired(
                'Waited {} seconds for mount process, but it timed out.'.format(self.CMD_TIMEOUT))

    def unmount(self):
        subprocess.run(['umount', '{}:/{}'.format(cf.env.NAS_HOST, cf.env.NAS_SHARED_DIR)])

    @property
    def is_mounted(self):
        p1 = subprocess.Popen(['mount'], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['awk', '{ print $1 }'], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        mnt_points = p2.communicate()[0].decode().strip().split('\n')

        return '{}:/{}'.format(cf.env.NAS_HOST, cf.env.NAS_SHARED_DIR) in mnt_points
