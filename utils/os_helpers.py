import tempfile
import shutil
import os


class TmpDir:
    def __enter__(self):
        self.dir = tempfile.mkdtemp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dir)

    def __str__(self):
        return self.dir


class Pushd:
    def __init__(self, new_dir):
        self.new_dir = new_dir

    def __enter__(self):
        self.previous_dir = os.getcwd()
        os.chdir(self.new_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.previous_dir)
