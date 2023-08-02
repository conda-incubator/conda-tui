from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from conda.base.constants import ROOT_ENV_NAME
from conda.base.context import context
from conda.common.path import paths_equal
from conda.core.envs_manager import list_all_known_prefixes as list_prefixes


@dataclass
class Environment:
    prefix: Path

    @property
    def relative_path(self) -> Path:
        return self._get_relative_path(self.prefix)

    @staticmethod
    @lru_cache
    def _get_relative_path(prefix: Path) -> Path:
        user_home = Path("~")
        return user_home / prefix.relative_to(user_home.expanduser())

    @property
    def name(self) -> str:
        """The name of the conda environment, if it is named. Otherwise, an empty string."""
        return self._get_name(self.prefix)

    @staticmethod
    @lru_cache
    def _get_name(prefix: Path) -> str:
        """Retrieve the name of the environment from its prefix, if it has a name.

        Otherwise, returns an empty string.

        Cached for performance.

        """
        if str(prefix) == context.root_prefix:
            return ROOT_ENV_NAME
        elif any(
            paths_equal(envs_dir, str(prefix.parent)) for envs_dir in context.envs_dirs
        ):
            return str(prefix.name)
        return ""

    def __hash__(self) -> int:
        return hash(self.prefix)


def list_environments() -> list[Environment]:
    """Get a list of conda environments installed on local machine."""
    return [Environment(prefix=Path(env)) for env in list_prefixes()]
