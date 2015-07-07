import subprocess


def execute_local_command(command):
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    out, err = p.communicate()
    return p.returncode, out, err


def execute_remote_command(remote_address, command):
    import paramiko

    class SilentPolicy(paramiko.WarningPolicy):
        def missing_host_key(self, client, hostname, key):
            pass

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(SilentPolicy())
    ssh_key = paramiko.RSAKey.from_private_key_file(remote_address['ssh_key'])
    ssh.connect(remote_address['host'], username=remote_address['user'], pkey=ssh_key, port=int(remote_address['port']),
                timeout=10)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    ssh_out = ssh_stdout.read()
    ssh_err = ssh_stderr.read()
    ssh_return_code = ssh_stdout.channel.recv_exit_status()
    ssh.close()
    return ssh_return_code, ssh_out, ssh_err


def execute_command(command, remote_address=None):
    if remote_address:
        return execute_remote_command(remote_address, command)
    return execute_local_command(command)
