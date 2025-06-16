from utils.services.env import EnvManager
from utils.services.file_writer import FileWriter
from utils.services.logger import Logger
from utils.services.perf_analyzer import PerfAnalyzer


class Services:
    def __init__(self, root_dir, logs_dir, enable_perf_analyzer, enable_logger):
        self._root_dir = root_dir
        self._logs_dir = logs_dir
        self._enable_perf_analyzer = enable_perf_analyzer
        self._enable_logger = enable_logger

    def __enter__(self, *args, **kwargs):
        self._env = EnvManager(self._root_dir)
        self._file_writer = FileWriter(self._env.home())
        self._perf_analyzer = PerfAnalyzer(self._env.get("PAI_SETUP_ROOT"), self._enable_perf_analyzer)
        self._logger = Logger(self._logs_dir, self._perf_analyzer, self._enable_logger)
        return self

    def __exit__(self, *args, **kwargs):
        """
        Service objects may require to be finalized to perform some cleanup operations or print
        their results.
        """
        self._env.finalize()
        self._file_writer.finalize()
        self._logger.finalize()
        self._perf_analyzer.finalize()  # Has to be last

    def assign_to(self, target):
        target._env = self._env
        target._file_writer = self._file_writer
        target._perf_analyzer = self._perf_analyzer
        target._logger = self._logger
