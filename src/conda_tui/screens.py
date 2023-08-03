from typing import Optional

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.screen import Screen as _Screen

from conda_tui.environment import Environment
from conda_tui.widgets import EnvironmentList
from conda_tui.widgets import Footer
from conda_tui.widgets import Header
from conda_tui.widgets import Logo
from conda_tui.widgets.table import PackageTableWidget


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
        yield PackageTableWidget(self.environment)

    def action_go_back(self) -> None:
        self.dismiss()
