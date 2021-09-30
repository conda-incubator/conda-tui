import json
import random
from pathlib import Path
from typing import Any
from typing import List

from conda.core.prefix_data import PrefixData

from conda_tui.environment import Environment


class Package:
    """Wrap a conda record, and supplement with custom attributes."""

    def __init__(self, record: PrefixData):
        self._record = record

    def __getattr__(self, item: str) -> Any:
        return getattr(self._record, item)

    @property
    def status(self) -> str:
        """A status string in console markup."""
        # TODO: Replace with real status
        if random.random() > 0.8:
            return "[blue]\u2B06[/blue] Upgrade to version [red]X.Y.Z[/red]"
        return "Up-to-date"

    @property
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
