import asyncio
from typing import Any

from rich.progress import Progress
from textual.widgets import Static

from conda_tui.package import Package


class PackageUpdateProgress(Static):
    def __init__(self, *args: Any, package: Package, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._package = package
        self._bar = Progress()

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_progress_bar)

    def update_progress_bar(self) -> None:
        self.update(self._bar)

    async def update_package(self):
        # TODO: This is a mock of actual package update
        with self._bar as bar:
            total_time, time_step = 2, 0.2
            task = bar.add_task("", total=int(total_time / time_step))
            while not bar.finished:
                bar.update(task, advance=1)
                await asyncio.sleep(time_step)
        self._package.update_available = False
        self.screen.dismiss(True)  # Return a value to trigger the callback
