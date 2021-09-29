from os.path import basename, dirname

from conda.core.envs_manager import list_all_known_prefixes
from conda.base.context import context
from conda.base.constants import ROOT_ENV_NAME
from conda.common.path import paths_equal
from rich import print


def get_name(prefix):
    if prefix == context.root_prefix:
        return ROOT_ENV_NAME
    elif any(
        paths_equal(envs_dir, dirname(prefix))
        for envs_dir in context.envs_dirs
    ):
        return basename(prefix)


envs = {}
for p in list_all_known_prefixes():
    envs.setdefault(get_name(p), []).append(p)
print(envs)