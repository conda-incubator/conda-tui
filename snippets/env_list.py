from os.path import basename
from os.path import dirname

from conda.base.constants import ROOT_ENV_NAME
from conda.base.context import context
from conda.common.path import paths_equal
from conda.core.envs_manager import list_all_known_prefixes


def get_name(prefix: str) -> str:
    if prefix == context.root_prefix:
        return ROOT_ENV_NAME
    elif any(paths_equal(envs_dir, dirname(prefix)) for envs_dir in context.envs_dirs):
        return basename(prefix)
    return ""


get_envs = list_all_known_prefixes


if __name__ == "__main__":
    from rich import print
    from rich.table import Table

    tbl = Table(title="envs")
    tbl.add_column("Name")
    tbl.add_column("Path")
    for env in get_envs():
        tbl.add_row(get_name(env), env)

    print(tbl)
