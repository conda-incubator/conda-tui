import json
import random
from functools import cached_property
from functools import lru_cache
from pathlib import Path
from typing import Any
from typing import List

from conda.core.prefix_data import PrefixData
from rich.console import Console
from rich.console import RenderableType
from rich.progress import BarColumn
from rich.progress import Progress
from rich.text import Text

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
    def status(self) -> RenderableType:
        try:
            if self._progress.finished:
                del self._progress
                del self._task

            self._progress.update(self._task, advance=1)
            return self._progress.get_renderable()
        except AttributeError:
            return self.get_icon(self.can_update) + " " + self.version

    @staticmethod
    @lru_cache
    def get_icon(can_update: bool) -> Text:
        if can_update:
            return Text.from_markup("[bold #DB6015]\u2191[/]")
        return Text.from_markup("[bold #43b049]\u2714[/]")

    def update(self, console: Console) -> None:
        if not self._can_update:
            return

        # TODO: do update here
        self._progress = Progress(BarColumn(bar_width=10), console=console)
        self._task = self._progress.add_task("Downloading", total=10)

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
