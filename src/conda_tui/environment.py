from dataclasses import dataclass
from functools import lru_cache
from os.path import basename
from os.path import dirname

from conda.base.constants import ROOT_ENV_NAME
from conda.base.context import context
from conda.common.path import paths_equal
from conda.core.envs_manager import list_all_known_prefixes as list_prefixes

# from os.path import expanduser
# from os.path import relpath


@dataclass
class Environment:
    prefix: str

    # @property
    # def rpath(self) -> Optional[str]:
    #     if self.path is None:
    #         return None
    #     return self.get_relative(self.path)
    #
    # @staticmethod
    # @lru_cache
    # def get_relative(prefix: str) -> str:
    #     return relpath(prefix, expanduser("~"))

    @property
    def name(self) -> str:
        """The name of the conda environment, if it is named. Otherwise, an empty string."""
        return self.get_name(self.prefix)

    @staticmethod
    @lru_cache
    def get_name(prefix: str) -> str:
        """Retrieve the name of the environment from its prefix, if it has a name.

        Otherwise, returns an empty string.

        Cached for performance.

        """
        if prefix == context.root_prefix:
            return ROOT_ENV_NAME
        elif any(
            paths_equal(envs_dir, dirname(prefix)) for envs_dir in context.envs_dirs
        ):
            return basename(prefix)
        return ""

    @property
    def label(self) -> str:
        return self.get_label(self.prefix, self.name)

    @staticmethod
    @lru_cache
    def get_label(prefix: str, name: str) -> str:
        """A nice string label for the environment, for rendering with terminal markdown."""
        if name:
            return f"[bold][green]{name}[/green][/bold] ({prefix})"
        return prefix

    def __hash__(self) -> int:
        return hash(self.prefix)


def list_environments() -> list[Environment]:
    """Get a list of conda environments installed on local machine."""
    return [Environment(prefix=env) for env in list_prefixes()]
