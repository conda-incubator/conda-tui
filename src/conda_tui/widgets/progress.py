import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import TaskProgressColumn
from rich.progress import TextColumn
from textual.widgets import Log
from textual.widgets import Static

from conda_tui.package import Package


class PackageUpdateProgress(Static):
    def __init__(self, *args: Any, package: Package, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._package = package
        self._bar = Progress()

    def on_mount(self) -> None:
        self.set_interval(1 / 60, lambda: self.update(self._bar))
        self.run_worker(self.update_package())

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


class ShellCommandProgress(Static):
    def __init__(self, *commands: str, **kwargs: Any):
        super().__init__(**kwargs)
        self._bar = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )

    def on_mount(self) -> None:
        self.set_interval(1 / 60, lambda: self.update(self._bar))

    async def run_command(self, command: list[str], log: Log):
        # Remove any existing tasks
        for task_id in self._bar.task_ids:
            self._bar.remove_task(task_id)

        with self._bar as bar:
            description = (
                f"Running command: [cyan bold]{' '.join(command)}[/cyan bold]:"
            )
            task = bar.add_task(description, total=None)

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir, "tmp.log")
                # Here, the subprocess writes to the temporary file, and then
                # the polling writes to the log widget. We do it this way so
                # it is not blocking.
                with tmp_path.open("w") as writer, tmp_path.open("r", 1) as reader:
                    process = subprocess.Popen(command, stdout=writer)
                    while process.poll() is None:
                        log.write(reader.read())
                    # Write any remaining characters
                    log.write(reader.read())
                log.write(f"\nFinished with status code {process.returncode}")

            bar.update(task, total=1, completed=True)
