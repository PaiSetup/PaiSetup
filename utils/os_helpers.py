import os
import shutil
import tempfile


class TmpDir:
    def __enter__(self):
        self._old_cwd = os.getcwd()
        self.dir = tempfile.mkdtemp()
        os.chdir(self.dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._old_cwd)
        shutil.rmtree(self.dir)

    def __str__(self):
        return self.dir


class Pushd:
    def __init__(self, new_dir):
        self.new_dir = new_dir

    def __enter__(self):
        self.previous_dir = os.getcwd()
        self.cd(self.new_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.previous_dir)

    def cd(self, new_dir):
        os.chdir(new_dir)
