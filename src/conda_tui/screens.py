import json
from typing import Any
from typing import Optional

from rich.json import JSON
from textual.app import ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.screen import Screen as _Screen
from textual.widgets import DataTable
from textual.widgets import Static

from conda_tui.environment import Environment
from conda_tui.package import Package
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
    package_map: dict[str, Package]

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield from super().compose()
        assert self.environment is not None, "Shouldn't be possible"
        table = DataTable()
        table.cursor_type = "row"
        table.add_columns("Name", "Description", "Version", "Build", "Channel")
        packages = list_packages_for_environment(self.environment)
        self.package_map = {}
        for row_num, pkg in enumerate(packages):
            table.add_row(
                pkg.name,
                pkg.description,
                pkg.status,
                pkg.build,
                pkg.schannel,
                key=pkg.name,
            )
            self.package_map[pkg.name] = pkg
        yield table

    def action_go_back(self) -> None:
        self.dismiss()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Push a new package detail screen when a package is selected."""
        screen = PackageDetailScreen(package=self.package_map[event.row_key.value])
        self.app.push_screen(screen)


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
