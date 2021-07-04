import os
import paramiko
from sshtunnel import open_tunnel
from stat import S_ISDIR

from config import Config
from utils import Logger

cf = Config.get_instance()
lg = Logger.get_logger()


class SSHException(Exception):
    pass


class SftpConnectException(Exception):
    pass


class SftpClientException(Exception):
    pass


class Sftp():

    # 秘密鍵を指定
    RSA_KEY = '~/.ssh/id_rsa'

    LOCAL_HOST = '127.0.0.1'
    LOCAL_PORT = 10022

    _env = {}
    _host = None
    _client = None
    _ssh_tunnel = None
    _sftp = None

    def __init__(self):

        env = {
            cf.HOST_NAMES[0]: {
                'SFTP_HOST': cf.env.SFTP_HOST1,
                'SFTP_PORT': cf.env.SFTP_PORT1,
                'SFTP_USER': cf.env.SFTP_USER1,
                'SFTP_PASSWORD': cf.env.SFTP_PASSWORD1,
                'SFTP_ROOT_PREFIXES': cf.env.SFTP_ROOT_PREFIXES1,
                'SSH_HOST': cf.env.SSH_HOST1,
                'SSH_PORT': cf.env.SSH_PORT1,
                'SSH_USER': cf.env.SSH_USER1,
                'SSH_PASSWORD': cf.env.SSH_PASSWORD1,
                'NAS_ROOT_PREFIXES': cf.env.NAS_ROOT_PREFIXES1,
            },
            # NOTE: ホストが増えたらここも増やす
            # cf.HOST_NAMES[1]: {
            #     'SFTP_HOST': cf.env.SFTP_HOST2,
            #     'SFTP_PORT': cf.env.SFTP_PORT2,
            #     'SFTP_USER': cf.env.SFTP_USER2,
            #     'SFTP_PASSWORD': cf.env.SFTP_PASSWORD2,
            #     'SFTP_ROOT_PREFIXES': cf.env.SFTP_ROOT_PREFIXES2,
            #     'SSH_HOST': cf.env.SSH_HOST2,
            #     'SSH_PORT': cf.env.SSH_PORT2,
            #     'SSH_USER': cf.env.SSH_USER2,
            #     'SSH_PASSWORD': cf.env.SSH_PASSWORD2,
            #     'NAS_ROOT_PREFIXES': cf.env.NAS_ROOT_PREFIXES2,
            # },
        }

        if cf.env.SFTP_LOG_ENABLED:
            paramiko_log = '{}/{}'.format(cf.LOGS_PATH, cf.env.SFTP_LOG_FILENAME)
            paramiko.util.log_to_file(paramiko_log, level=cf.env.SFTP_LOG_LEVEL)

        self._env = env

    def __get_interactive_handlar(self, pasword):
        def handlar(title, instructions, fields):
            rep = []
            if len(fields) > 0 and len(fields[0]) > 0 and \
               str(fields[0][0]).strip() == 'Password:':
                rep.append(pasword)
            return tuple(rep)
        return handlar

    def connect(self, host):
        self.close()

        try:
            ssh_tunnel = open_tunnel(
                (self._env[host]['SSH_HOST'], self._env[host]['SSH_PORT']),
                ssh_username=self._env[host]['SSH_USER'],
                ssh_password=self._env[host]['SSH_PASSWORD'],
                ssh_pkey=self.RSA_KEY,
                remote_bind_address=(self._env[host]['SFTP_HOST'], self._env[host]['SFTP_PORT']),
                local_bind_address=(self.LOCAL_HOST, self.LOCAL_PORT)
            )
        except paramiko.ssh_exception.SSHException as e:
            raise SSHException('ssh authentication failure.')

        ssh_tunnel.start()

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            trans = paramiko.Transport(ssh_tunnel.local_bind_address)
            trans.connect(username=self._env[host]['SFTP_USER'])
            trans.auth_interactive(
                self._env[host]['SFTP_USER'],
                self.__get_interactive_handlar(self._env[host]['SFTP_PASSWORD'])
                )
        except paramiko.ssh_exception.AuthenticationException as e:
            raise SftpConnectException('sftp authentication failure.')

        sftp = paramiko.SFTPClient.from_transport(trans)

        self._client = client
        self._ssh_tunnel = ssh_tunnel
        self._sftp = sftp
        self._host = host

    def get(self, lpath, rpath):
        if self._host is None:
            raise SftpClientException('SFTP connection isn\'t established.')

        lg.info('-' * 30)
        lg.info('remote_dir:\t{}:{}'.format(self._env[self._host]['SFTP_HOST'], rpath))
        lg.info('-' * 30)

        self._local_mkdirs(lpath)
        self._exec_sftp('get', lpath, rpath)

    def _exec_sftp(self, method, lpath, rpath):
        self._sftp.chdir(rpath)

        for directory in self._sftp.listdir_attr():
            if cf.SFTP_EXCLUDE_DIR == directory.filename:
                continue

            if S_ISDIR(directory.st_mode):
                new_lpath = '{}/{}'.format(lpath, directory.filename)
                new_rpath = '{}/{}'.format(rpath, directory.filename)
                self._local_mkdirs(new_lpath)
                self._exec_sftp(method, new_lpath, new_rpath)
            else:
                self._sftp.chdir(rpath)
                try:
                    pass
                    self._sftp.get(
                        directory.filename,
                        os.path.join(lpath, directory.filename),
                    )
                except Exception as e:
                    lg.critical('An unexpected error has occurred.')

                lg.info('backup {}'.format(os.path.join(rpath, directory.filename)))

    def _local_mkdirs(self, lpath):
        os.makedirs(lpath, exist_ok=True)

    def close(self):
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None
        if self._client is not None:
            self._client.close()
            self._client = None
        if self._ssh_tunnel is not None:
            self._ssh_tunnel.stop()
            self._ssh_tunnel = None
        self._host = None
