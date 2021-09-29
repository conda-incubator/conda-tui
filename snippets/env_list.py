from os.path import basename
from os.path import dirname
from typing import Any
from typing import Dict

from conda.base.constants import ROOT_ENV_NAME
from conda.base.context import context
from conda.common.path import paths_equal
from conda.core.envs_manager import list_all_known_prefixes
from rich import print


def get_name(prefix: str) -> str:
    if prefix == context.root_prefix:
        return ROOT_ENV_NAME
    elif any(paths_equal(envs_dir, dirname(prefix)) for envs_dir in context.envs_dirs):
        return basename(prefix)
    return ""


envs: Dict[str, Any] = {}
for p in list_all_known_prefixes():
    envs.setdefault(get_name(p), []).append(p)
print(envs)
