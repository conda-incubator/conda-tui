import json
import random
from contextlib import suppress
from functools import cache
from functools import cached_property
from pathlib import Path
from typing import Any

from conda.core.prefix_data import PrefixData
from rich.console import Console
from rich.console import RenderableType
from rich.progress import BarColumn
from rich.progress import Progress
from rich.text import Text
from textual.events import Timer

from conda_tui.environment import Environment


class Package:
    """Wrap a conda PrefixRecord, and supplement with custom attributes."""

    def __init__(self, record: PrefixData):
        self._record = record
        # TODO: This should be replaced with a call to the conda repo
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
                if self._sleep > 2:
                    del self._progress
                    del self._task
                    del self._sleep
                    del self._timer
                else:
                    self._sleep += 1

            return self._progress.get_renderable()
        except AttributeError:
            return self._get_update_status_icon(self.can_update) + " " + self.version

    def increment(self) -> None:
        with suppress(AttributeError):
            self._progress.advance(self._task)

    @staticmethod
    @cache
    def _get_update_status_icon(can_update: bool) -> Text:
        if can_update:
            return Text.from_markup("[bold #DB6015]\N{UPWARDS ARROW}[/]")
        return Text.from_markup("[bold #43b049]\N{HEAVY CHECK MARK}[/]")

    def update(self, console: Console, timer: Timer) -> None:
        if not self._can_update:
            return

        # TODO: do update here
        self._progress = Progress(BarColumn(bar_width=10), console=console)
        self._task = self._progress.add_task("Downloading", total=20)
        self._sleep = 0
        self._timer = timer

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
        info_path = Path(package_dir, "info", "about.json")
        if not info_path.exists():
            return ""
        with info_path.open("r") as fh:
            return json.load(fh).get("summary", "")


@cache
def list_packages_for_environment(env: Environment) -> list[Package]:
    prefix_data = PrefixData(str(env.prefix), pip_interop_enabled=True)
    packages = [Package(record) for record in prefix_data.iter_records()]
    return sorted(packages, key=lambda x: x.name)
