import os
import shutil
import stat
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.os_function import linux_only, windows_only
from utils.services.file_writer import FileType


class SshStep(Step):
    def __init__(self, secret_dir, full):
        super().__init__("Ssh")
        self._full = full
        self._secret_dir = secret_dir

    @windows_only
    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    @linux_only
    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("openssh")
        dependency_dispatcher.register_homedir_file(".ssh")

    def perform(self):
        src_ssh_key_path = self._find_ssh_key()
        if src_ssh_key_path is None:
            self._logger.push_warning("Could not find ssh key")
            return

        ssh_dir = self._env.home() / ".ssh"
        ssh_config_path = ssh_dir / "config"
        ssh_known_hosts_path = ssh_dir / "known_hosts"
        ssh_key_path = ssh_dir / src_ssh_key_path.stem
        ssh_public_key_path = ssh_key_path.with_suffix(".pub")

        self._logger.log("Setting ssh config")
        self._file_writer.write_lines(
            ssh_config_path,
            [
                f"IdentityFile {ssh_key_path}",
                "",
                "Host github.com bitbucket.org",
                "    User DziubanMaciej",
            ],
            file_type=FileType.ConfigFile,
        )

        self._logger.log(f"Copying ssh key {src_ssh_key_path} -> {ssh_key_path}")
        shutil.copy(src_ssh_key_path, ssh_key_path)

        self._logger.log(f"Generating public key {ssh_public_key_path} from private key")
        public_key_command = f'ssh-keygen -f "{ssh_key_path}" -y'
        public_key = run_command(public_key_command, stdout=Stdout.return_back()).stdout
        self._file_writer.write_lines(ssh_public_key_path, [public_key], file_type=FileType.ConfigFileNoComments)

        if self._full or not ssh_known_hosts_path.exists():
            self._logger.log("Setting up known_hosts for typical sites")
            known_hosts_command = "ssh-keyscan github.com"
            known_hosts = run_command(known_hosts_command, stdout=Stdout.return_back()).stdout.splitlines()
            self._file_writer.write_lines(ssh_known_hosts_path, known_hosts, file_type=FileType.ConfigFileNoComments)

        self._logger.log(f"Setting permissions for ssh files (read-write only for the user {self._env.get('USER')})")
        os.chmod(ssh_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.chmod(ssh_config_path, stat.S_IRUSR | stat.S_IWUSR)
        os.chmod(ssh_known_hosts_path, stat.S_IRUSR | stat.S_IWUSR)
        os.chmod(ssh_key_path, stat.S_IRUSR | stat.S_IWUSR)
        os.chmod(ssh_public_key_path, stat.S_IRUSR | stat.S_IWUSR)

    def _find_ssh_key(self):
        for file in self._secret_dir.iterdir():
            if file.suffix == ".ssh":
                return file
        return None
