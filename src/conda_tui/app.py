from functools import cache
from pathlib import Path
from typing import Any

# from rich.console import RenderableType
from rich.text import Text
from textual.app import App
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView
from textual.widgets import Static

# from conda_tui.environment import Environment
from conda_tui.environment import list_environments
from conda_tui.widgets import Footer
from conda_tui.widgets import Header

# from textual.events import Mount
# from textual.reactive import Reactive
# TODO: We need to get rid of this private import
# from textual.widgets._tree_control import TreeNode, TreeControl
# from textual.scroll_view import ScrollView

# from conda_tui.package import list_packages_for_environment
# from conda_tui.table import PackageTableWidget

HERE = Path(__file__).parent


class Logo(Static):
    """A static display of the conda logo"""

    LOGO_PATH = Path(HERE, "resources", "ascii-logo-80.txt")

    def __init__(self, **kwargs: Any):
        super().__init__(renderable=self.get_logo(), **kwargs)

    @cache
    def get_logo(self) -> Text:
        """Load the text for the ASCII art.

        Ensure all lines same length and beginning with blank non-whitespace character.

        """
        with self.LOGO_PATH.open("r") as fp:
            lines = fp.read().split("\n")

        max_line_length = max(len(line) for line in lines)
        blank = "\N{ZERO WIDTH SPACE}"  # A blank non-whitespace character so Rich can center the logo
        padded_lines = [f"{blank}{line:{max_line_length}s}{blank}" for line in lines]

        logo_text = Text("\n".join(padded_lines))
        return logo_text


class EnvironmentList(Static):
    def compose(self) -> ComposeResult:
        """Generate a static list view of all conda environments"""
        items = []
        for env in list_environments():
            # TODO: Black/White should be based on hover
            if env.name:
                label = f"\N{BLACK CIRCLE} [bold][green]{env.name}[/green][/bold] ({env.relative_path})"
            else:
                label = f"\N{WHITE CIRCLE} {env.relative_path}"
            items.append(ListItem(Label(label)))
        yield Static("Environment List", classes="center")
        yield ListView(*items)


class CondaTUI(App):
    """A hacked-together Conda Text User Interface (TUI)."""

    TITLE = "conda-tui"
    CSS_PATH = Path("styles.css")
    BINDINGS = [
        ("h", "go_home", "Home"),
        ("e", "show_environment_list", "Environments"),
        ("q", "quit", "Quit"),
    ]

    show_logo = reactive(True)
    show_environment_list = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Logo(id="logo")
        yield EnvironmentList(classes="hidden", id="environment-list")
        yield Footer()

    def action_go_home(self):
        self.show_logo = True
        self.show_environment_list = False

    def action_show_environment_list(self):
        self.show_logo = False
        self.show_environment_list = True

    def watch_show_logo(self, show_logo: bool) -> None:
        """Hide or un-hide logo based on show_logo reactive variable."""
        logo = self.query_one("#logo")
        if show_logo:
            logo.remove_class("hidden")
        else:
            logo.add_class("hidden")

    def watch_show_environment_list(self):
        """Hide or un-hide environment list based on show_environment_list reactive variable."""
        env_list = self.query_one("#environment-list")
        if self.show_environment_list:
            env_list.remove_class("hidden")
        else:
            env_list.add_class("hidden")

    # async def on_mount(self) -> None:
    #     """Call after terminal goes in to application mode."""
    #
    #     self.environment_list = ScrollView(EnvironmentTree())
    #     await self.view.dock(
    #         self.environment_list, edge="left", size=30, name="sidebar"
    #     )
    #
    #     self.package_list = ScrollView(get_logo())
    #     await self.view.dock(self.package_list, edge="right")
    #
    # async def handle_tree_click(self, message) -> None:
    #     """Display the package list if the environment exists."""
    #     if not message.node.data.path:
    #         return
    #
    #     # if not message.node.loaded:
    #     await self.show_package_table(message.node)
    #     await message.node.expand()
    #
    # async def action_display_logo(self) -> None:
    #     """Display the logo when "H" is pressed."""
    #     await self.package_list.update(get_logo())

    # async def show_package_table(self, node: TreeNode[Environment]) -> None:
    #     """Update the package list table based on selected environment."""
    #     packages = list_packages_for_environment(node.data)
    #     await self.package_list.update(PackageTableWidget(node.data, packages))


def run() -> None:
    """Run the application."""
    CondaTUI().run()
