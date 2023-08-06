from steps.step import Step
from utils import command
from utils.log import log
from pathlib import Path
from utils.file_writer import FileType
import shutil
import os
import stat


class SshStep(Step):
    def __init__(self, secret_dir):
        super().__init__("Ssh")
        self._secret_dir = secret_dir

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    def perform(self):
        src_ssh_key_path = self._find_ssh_key()
        if src_ssh_key_path is None:
            log("Could not find ssh key")
            return

        ssh_dir = self._env.home() / ".ssh"
        ssh_config_path = ssh_dir / "config"
        ssh_known_hosts_path = ssh_dir / "known_hosts"
        ssh_key_path = ssh_dir / src_ssh_key_path.stem
        ssh_public_key_path = ssh_key_path.with_suffix(".pub")

        log("Setting ssh config")
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

        log(f"Copying ssh key {src_ssh_key_path} -> {ssh_key_path}")
        shutil.copy(src_ssh_key_path, ssh_key_path)

        log(f"Generating public key {ssh_public_key_path} from private key")
        public_key_command = f'ssh-keygen -f "{ssh_key_path}" -y'
        public_key = command.run_command(public_key_command, return_stdout=True)
        self._file_writer.write_lines(ssh_public_key_path, [public_key], file_type=FileType.ConfigFileNoComments)

        log("Setting up known_hosts for typical sites")
        known_hosts_command = "ssh-keyscan github.com"
        known_hosts = command.run_command(known_hosts_command, return_stdout=True).splitlines()
        self._file_writer.write_lines(ssh_known_hosts_path, known_hosts, file_type=FileType.ConfigFileNoComments)

        log(f"Setting permissions for ssh files (read-write only for the user {self._env.get('USER')})")
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