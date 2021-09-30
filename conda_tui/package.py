import json
import random
from functools import cached_property
from functools import lru_cache
from pathlib import Path
from typing import Any
from typing import List

from conda.core.prefix_data import PrefixData

from conda_tui.environment import Environment


class Package:
    """Wrap a conda record, and supplement with custom attributes."""

    def __init__(self, record: PrefixData):
        self._record = record
        self._update: bool = bool(random.random() > 0.8)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._record, item)

    @property
    def status(self) -> str:
        """A status string in console markup."""
        return self.get_status(self._update)

    @staticmethod
    @lru_cache
    def get_status(can_update: bool) -> str:
        # TODO: Replace with real status
        if can_update:
            return "[blue]\u2b06[/blue] Upgrade to version [red]X.Y.Z[/red]"
        return "[green]\u2714[/green] Up-to-date"

    def update(self) -> None:
        # TODO: do update here
        self._update = False

    @cached_property
    def description(self) -> str:
        """Attempt to load the package description."""
        try:
            package_dir = self.extracted_package_dir
        except AttributeError:
            return ""
        with Path(package_dir, "info", "about.json").open("r") as fh:
            return json.load(fh).get("summary", "")


def list_packages_for_environment(env: Environment) -> List[Package]:
    prefix_data = PrefixData(env.path, pip_interop_enabled=True)
    packages = [Package(record) for record in prefix_data.iter_records()]
    return sorted(packages, key=lambda x: x.name)
