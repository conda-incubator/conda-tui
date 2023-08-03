from typing import Optional

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.screen import Screen as _Screen
from textual.widgets import DataTable

from conda_tui.environment import Environment
from conda_tui.package import list_packages_for_environment
from conda_tui.widgets import EnvironmentList
from conda_tui.widgets import Footer
from conda_tui.widgets import Header
from conda_tui.widgets import Logo


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

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield from super().compose()
        assert self.environment is not None, "Shouldn't be possible"
        yield DataTable()

    def on_mount(self) -> None:
        """Load the packages for the environment and populate the table."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Name", "Description", "Version", "Build", "Channel")
        packages = list_packages_for_environment(self.environment)
        for row_num, pkg in enumerate(packages):
            table.add_row(
                pkg.name,
                pkg.description,
                pkg.status,
                pkg.build,
                pkg.schannel,
                key=pkg.name,
            )

    def action_go_back(self) -> None:
        self.dismiss()
