import os
import sys
import datetime
import argparse

from config import Config
from utils import Logger, Mount, Sftp

cf = Config.get_instance()
lg = Logger.get_logger()


def main(args):
    is_dry = args.dry
    is_verbose = args.verbose

    lg.info('-' * 60)
    lg.info('{} start.'.format(os.path.basename(sys.argv[0])))
    lg.info('-' * 30)
    lg.info('version:\t{}'.format(cf.env.APP_VERSION))
    lg.info('dry:\t{}'.format(is_dry))
    lg.info('verbose:\t{}'.format(is_verbose))
    lg.info('-' * 30)

    if is_verbose:
        print('debug')
        lg.setLevel(logging.DEBUG)

    mnt = Mount()
    for cnt in range(cf.NAS_RETRY_COUNT):
        if mnt.is_mounted:
            break
        mnt.mount()

    if not mnt.is_mounted:
        lg.warning('NAS volume is not mounted.')
        raise Exception('NAS volume is not mounted.')

    dt_now = datetime.datetime.now(datetime.timezone.utc)
    nas_dir = dt_now.strftime(cf.NAS_DIR_FORMAT)

    hosts = cf.HOST_NAMES

    sftp = Sftp()

    for host in hosts:
        sftp.connect(host)

        prefiexs = []
        if host == cf.hosts[0]:
            prefiexs.append(str_to_list(cf.env.NAS_ROOT_PREFIXES1))
            prefiexs.append(str_to_list(cf.env.SFTP_ROOT_PREFIXES1))

        # NOTE: ホストが増えたらここも増やす
        # if host == cf.hosts[1]:
        #     prefiexs.append(str_to_list(cf.env.NAS_ROOT_PREFIXES2))
        #     prefiexs.append(str_to_list(cf.env.SFTP_ROOT_PREFIXES2))

        for lpath, rpath in zip(*prefiexs):
            if lpath == '' or rpath == '':
                continue

            lpath = '/{}/{}/{}'.format(cf.NAS_MOUNTED_POINT, lpath, nas_dir)
            rpath = '/{}'.format(rpath)

            sftp.get(lpath, rpath)

    sftp.close()

    for cnt in range(cf.NAS_RETRY_COUNT):
        if mnt.is_mounted:
            mnt.unmount()

    lg.info('{} done.'.format(os.path.basename(sys.argv[0])))


def str_to_list(arg):
    if isinstance(arg, str):
        return [arg]
    return arg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-d',
        '--dry',
        help='Show what would have been executed',
        action='store_true')
    parser.add_argument(
        '-v',
        '--verbose',
        help='Increase verbosity',
        action='store_true')

    args = parser.parse_args()
    main(args)
