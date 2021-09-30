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
        self._can_update: bool = bool(random.random() > 0.8)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._record, item)

    @property
    def can_update(self) -> bool:
        return self._can_update

    @property
    def icon(self) -> str:
        return self.get_icon(self.can_update)

    @staticmethod
    @lru_cache
    def get_icon(can_update: bool) -> str:
        if can_update:
            return "[bold #DB6015]\u2191[/]"
        return "[bold #43b049]\u2714[/]"

    def update(self) -> None:
        if not self._can_update:
            return

        # TODO: do update here

        # mock version incrementing
        self.version = "X.Y.Z"

        self._can_update = False

    @cached_property
    def description(self) -> str:
        """Attempt to load the package description."""
        try:
            package_dir = self.extracted_package_dir
        except AttributeError:
            return ""
        with Path(package_dir, "info", "about.json").open("r") as fh:
            return json.load(fh).get("summary", "")


@lru_cache
def list_packages_for_environment(env: Environment) -> List[Package]:
    prefix_data = PrefixData(env.path, pip_interop_enabled=True)
    packages = [Package(record) for record in prefix_data.iter_records()]
    return sorted(packages, key=lambda x: x.name)
