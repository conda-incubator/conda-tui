from typing import List

from conda.core.prefix_data import PrefixData

from conda_tui.environment import Environment


class Package(PrefixData):
    pass


def list_packages_for_environment(env: Environment) -> List[Package]:
    return sorted(
        Package(env.path, pip_interop_enabled=True).iter_records(),
        key=lambda x: x.name,
    )
