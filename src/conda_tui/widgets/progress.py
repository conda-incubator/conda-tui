from typing import Any

from rich.progress import BarColumn
from rich.progress import Progress
from textual.widgets import Static

from conda_tui.package import Package


class PackageUpdateProgress(Static):
    def __init__(self, *args: Any, package: Package, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._package = package
        self._bar = Progress(BarColumn(bar_width=60))
        self._task = self._bar.add_task("", total=None)

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_progress_bar)

    def update_progress_bar(self) -> None:
        self.update(self._bar)
