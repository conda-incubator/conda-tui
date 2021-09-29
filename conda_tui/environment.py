from dataclasses import dataclass
from functools import lru_cache
from os.path import basename
from os.path import dirname
from typing import List

from conda.base.constants import ROOT_ENV_NAME
from conda.base.context import context
from conda.common.path import paths_equal
from conda.core.envs_manager import list_all_known_prefixes


@dataclass
class Environment:
    path: str

    @property
    def name(self) -> str:
        try:
            return self.__name
        except AttributeError:
            self.__name: str = self.get_name(self.path)
            return self.__name

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


get_envs = list_all_known_prefixes


def list_environments() -> List[Environment]:
    """Get a list of conda environments installed on local machine."""

    return [Environment(env) for env in get_envs()]
