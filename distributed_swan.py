"""Script Docstring"""

__author__ = 'Tim Woods'
__copyright__ = 'Copyright (c) 2018, Tim Woods'
__license__ = 'MIT'

import json
import os
import time
import argparse
import paramiko

JOB_FILENAME = 'jobs.txt'
LOCK_FILENAME = 'lock.lock'
SKAGIT_OP_PATH = os.getcwd()

HOST_LIST = ['c-0-%d' % x for x in range(8)]


class Host:
    def __init__(self, hostname):
        self.name = hostname
        self.working = False
        self.ssh_client = None

    def ssh_into_node(self, credentials_dict):
        k = paramiko.RSAKey.from_private_key_file(
            credentials_dict['rsa_filepath'],
            password=credentials_dict['password'])
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.name,
                    username=credentials_dict['username'],
                    pkey=k)

    def disconnect(self):
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None
            self.working = False

    def exec_command(self, command):
        self.working = True
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        self.working = False


class Hosts:
    def __init__(self, host_list, cred_dict):
        self.hosts = []
        self._hosts_from_list(host_list)
        self.credentials = cred_dict
        self.next = 0

    def next_host(self):
        host = self.hosts[self.next % len(self.hosts)]
        self.next += 1
        return host

    def _hosts_from_list(self, host_list):
        for host in host_list:
            self.hosts.append(Host(host))

    def all_working(self):
        status_list = [host.working for host in self.hosts]
        return all(status_list)

    def init_all_hosts(self):
        for host in self.hosts:
            host.ssh_into_node(self.credentials)

    def close_all_hosts(self):
        for host in self.hosts:
            host.disconnect()


def create_job_file():
    jobs = '\n'.join([str(x) for x in range(48)])
    with open(JOB_FILENAME, 'w') as job_file:
        job_file.write(jobs)


def create_lock_file():
    with open(LOCK_FILENAME, 'w') as lock:
        lock.write('locked')


def delete_lock_file():
    os.remove(LOCK_FILENAME)


def pop_from_job_file():
    while os.path.exists(LOCK_FILENAME):
        time.sleep(1)

    create_lock_file()

    with open(JOB_FILENAME, 'r') as job_file:
        jobs = job_file.readlines()
        job = jobs[0] if jobs else None
        remaining = jobs[1:] if jobs else None

    if remaining:
        with open(JOB_FILENAME, 'w') as job_file:
            job_file.writelines(remaining)
    else:
        os.remove(JOB_FILENAME)

    delete_lock_file()
    return int(job)


def create_swan_runs():
    def swan_run_from_dir(directory):
        return '\n'.join([set_path, 'cd {}'.format(directory), run_swan])

    swan_path = os.path.join(SKAGIT_OP_PATH, 'SWAN_runs')
    swan_dirs = [os.path.join(swan_path, 'SWAN_{}').format(x) for x in range(48)]
    set_path = 'export PATH=$PATH:/home/woodst/SWAN/swan4120'
    run_swan = 'swanrun -input input.swn -omp 12'
    return [swan_run_from_dir(dir) for dir in swan_dirs]


def display_credentials_error():
    print('''Error loading credentials - expected JSON file with:
          {
            "username": user's username,
            "password": user's password, or RSA public key password,
            "rsa_filepath": absolute path to user's public SSH key,
            "use_rsa": true or false
          }''')
    exit(1)


def display_host_error():
    print('''Error reading hostfile - expected text file with:
    c-0-0
    c-0-1
    and so on for each hostname for compute nodes
    on which to run SWAN''')
    exit(1)


def load_credentials(credentials_filename):
    try:
        with open(credentials_filename, 'r') as cred_file:
            return json.load(cred_file)
    except json.JSONDecodeError:
        display_credentials_error()


def load_hosts(host_filename):
    try:
        with open(host_filename, 'r') as host_file:
            return json.load(host_file)
    except json.JSONDecodeError:
        display_host_error()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='SSH Credentials filename - a JSON file', type=str)
    parser.add_argument('-h', help='File containing a list of line-delimited host names', type=str)
    return parser.parse_args()


def main():
    args = parse_args()
    creds = load_credentials(args.c)
    create_job_file()
    swan_runs = create_swan_runs()
    run_by_idx = {a: b for a, b in zip(range(48), swan_runs)}
    h = Hosts(HOST_LIST, creds)
    h.init_all_hosts()
    try:
        while os.path.exists(JOB_FILENAME):
            while h.all_working():
                time.sleep(1)
            job = run_by_idx[pop_from_job_file()]
            h.next_host().exec_command(job)

    finally:
        h.close_all_hosts()


if __name__ == '__main__':
    main()
