from pathlib import Path
from typing import Optional

from textual.app import App
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.screen import Screen as _Screen

from conda_tui.environment import Environment
from conda_tui.widgets import EnvironmentList
from conda_tui.widgets import Footer
from conda_tui.widgets import Header
from conda_tui.widgets import Logo

# from textual.widgets._tree_control import TreeNode, TreeControl
# from textual.scroll_view import ScrollView

# from conda_tui.package import list_packages_for_environment
# from conda_tui.table import PackageTableWidget


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
        # TODO: This is just placeholder text for now
        from rich.text import Text
        from textual.widgets import Static

        if self.environment is not None:
            yield Static(Text(str(self.environment.prefix)))

    def action_go_back(self) -> None:
        self.dismiss()


class CondaTUI(App):
    """A hacked-together Conda Text User Interface (TUI)."""

    TITLE = "conda-tui"
    CSS_PATH = Path("styles.css")
    SCREENS = {
        "home": HomeScreen(),
        "environments": EnvironmentScreen(),
        "package_list": PackageListScreen(),
    }
    BINDINGS = [
        ("h", "switch_screen('home')", "Home"),
        ("e", "switch_screen('environments')", "Environments"),
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """When we start up, push the home screen.

        This allows us to use switch_screen to switch between the various views without
        having an infinitely-growing screen stack.

        """
        self.push_screen("home")

    # async def on_mount(self) -> None:
    #     """Call after terminal goes in to application mode."""
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
