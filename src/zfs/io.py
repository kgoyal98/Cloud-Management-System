"""
Helper functions to interact with the filesystem. Since there is seemingly no official
API or project to interact with ZFS.
"""


from typing import List, Any, Iterator, cast
from contextlib import contextmanager, AbstractContextManager
from subprocess import Popen, PIPE

import re
import os


newlines = re.compile(r'\n+')


@contextmanager
def _getIO(command: str) -> Iterator:
    """
    Get results from terminal commands as lists of lines of text.
    """
    with Popen(command, shell=True, stdout=PIPE, stderr=PIPE) as proc:
        stdout, stderr = proc.communicate()

    if stderr:
        yield stderr, os.EX_IOERR

    if stdout:
        _stdout: List[str] = re.split(newlines, stdout.decode())

        # For some reason, `shell=True` likes to yield an empty string.
        _stdout = cast(List[str], stdout[:-1] if _stdout[-1] == '' else _stdout)

    yield _stdout, os.EX_OK


class ZFS(AbstractContextManager):
    """
    Helpful methods for interacting with the filesystem in a particular pool.
    """
    def __init__(self, poolName: str) -> None:
        self.poolName = poolName

    def __enter__(self) -> ZFS:
        return self

    def __exit__(self, *args: Any) -> None:
        return

    # Get information about the filesystem's datasets.
    def datasetExists(self, dataset: str) -> bool:
        """
        Determine whether or not a dataset exists in the provided ZPool.
        """
        with _getIO(f'zfs list -H {dataset}') as sh:
            _, exitCode = sh
            return exitCode == os.EX_OK

    def datasetHasSnapshots(self, dataset: str) -> bool:
        """
        Determine whether or not a dataset has snapshots.
        """
        with _getIO(f'zfs list -Hrt snapshot {dataset}') as sh:
            msg, exitCode = sh
            return exitCode == os.EX_OK or str(msg) == ''
