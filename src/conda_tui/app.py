from pathlib import Path

from textual.app import App
from textual.app import ComposeResult
from textual.reactive import reactive

from conda_tui.widgets import EnvironmentList
from conda_tui.widgets import Footer
from conda_tui.widgets import Header
from conda_tui.widgets import Logo

# from textual.widgets._tree_control import TreeNode, TreeControl
# from textual.scroll_view import ScrollView

# from conda_tui.package import list_packages_for_environment
# from conda_tui.table import PackageTableWidget


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

    def action_go_home(self) -> None:
        self.show_logo = True
        self.show_environment_list = False

    def action_show_environment_list(self) -> None:
        self.show_logo = False
        self.show_environment_list = True

    def watch_show_logo(self, show_logo: bool) -> None:
        """Hide or un-hide logo based on show_logo reactive variable."""
        logo = self.query_one("#logo")
        if show_logo:
            logo.remove_class("hidden")
        else:
            logo.add_class("hidden")

    def watch_show_environment_list(self) -> None:
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
