import json
from typing import Any
from typing import Optional

from rich.json import JSON
from textual.app import ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.screen import Screen as _Screen
from textual.widgets import DataTable
from textual.widgets import Footer
from textual.widgets import Log
from textual.widgets import Static

from conda_tui.environment import Environment
from conda_tui.package import Package
from conda_tui.package import list_packages_for_environment
from conda_tui.widgets import EnvironmentList
from conda_tui.widgets import Header
from conda_tui.widgets import Logo
from conda_tui.widgets import PackageUpdateProgress
from conda_tui.widgets.progress import ShellCommandProgress


class Screen(_Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()


class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Logo(id="logo")


class EnvironmentScreen(Screen):
    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield EnvironmentList(id="environment-list")


class PackageListScreen(Screen):
    """A screen to display the packages installed into a specific environment."""

    environment = reactive[Optional[Environment]](None)
    packages: list[Package]

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("u", "update_package", "Update"),
    ]

    def compose(self) -> ComposeResult:
        yield from super().compose()
        assert self.environment is not None, "Shouldn't be possible"
        table = DataTable()
        table.cursor_type = "row"
        table.add_columns("Name", "Description", "Version", "Build", "Channel")
        self.packages = list_packages_for_environment(self.environment)
        for row_num, pkg in enumerate(self.packages):
            table.add_row(
                pkg.name,
                pkg.description,
                pkg.status,
                pkg.build,
                pkg.schannel,
                key=pkg.name,
            )
        yield table

    def action_go_back(self) -> None:
        self.dismiss()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Push a new package detail screen when a package is selected."""
        self.app.push_screen(
            PackageDetailScreen(package=self.packages[event.cursor_row])
        )

    def action_update_package(self):
        """Launch a new screen to display package update progress."""
        table = self.query_one(DataTable)
        row_num = table.cursor_row
        package = self.packages[row_num]

        def update_package_status(was_success: bool):
            if was_success:
                table.update_cell_at((row_num, 2), package.status)

        self.app.push_screen(
            PackageUpdateScreen(package=package), update_package_status
        )


class PackageUpdateScreen(Screen):
    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, *args: Any, package: Package, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._package = package

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Static(f"Updating package [cyan bold]`{self._package.name}`[/cyan bold]")
        yield Static("[red bold]TODO[/red bold]: Hook this up to actual download")
        yield PackageUpdateProgress(package=self._package)

    def action_go_back(self):
        self.dismiss()


class ShellCommandScreen(Screen):
    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, command: list[str], **kwargs: Any):
        super().__init__(**kwargs)
        self._command = command

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield ShellCommandProgress()
        yield Log(highlight=True, id="shell-command-log")

    def on_screen_resume(self) -> None:
        log = self.query_one("#shell-command-log")
        log.clear()
        progress = self.query_one(ShellCommandProgress)
        self.run_worker(progress.run_command(self._command, log=log))

    def action_go_back(self):
        self.dismiss()


class PackageDetailScreen(Screen):
    """A screen to display the details of a package."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, *args: Any, package: Package, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._package = package

    def compose(self) -> ComposeResult:
        # TODO: This is just a simple JSON dump, should be nicer.
        yield from super().compose()
        yield Grid(
            Static(
                f"Package details for [cyan bold]`{self._package.name}`[/cyan bold]:"
            ),
            Static(JSON(json.dumps(self._package.dist_fields_dump()))),
            id="package-details",
        )

    def action_go_back(self):
        self.dismiss()
