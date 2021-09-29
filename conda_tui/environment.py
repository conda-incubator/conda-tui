from dataclasses import dataclass
from functools import lru_cache
from os.path import basename
from os.path import dirname
from os.path import expanduser
from os.path import relpath
from typing import List
from typing import Optional

from conda.base.constants import ROOT_ENV_NAME
from conda.base.context import context
from conda.common.path import paths_equal
from conda.core.envs_manager import list_all_known_prefixes


@dataclass
class Environment:
    path: Optional[str] = None

    @property
    def rpath(self) -> Optional[str]:
        if self.path is None:
            return None
        return self.get_relative(self.path)

    @staticmethod
    @lru_cache
    def get_relative(prefix: str) -> str:
        return relpath(prefix, expanduser("~"))

    @property
    def name(self) -> Optional[str]:
        if self.path is None:
            return None
        return self.get_name(self.path)

    @staticmethod
    @lru_cache
    def get_name(prefix: str) -> str:
        if prefix == context.root_prefix:
            return ROOT_ENV_NAME
        elif any(
            paths_equal(envs_dir, dirname(prefix)) for envs_dir in context.envs_dirs
        ):
            return basename(prefix)
        return ""


def get_envs() -> List[Environment]:
    """Get a list of conda environments installed on local machine."""

    return [Environment(env) for env in list_all_known_prefixes()]
