from functools import lru_cache
from pathlib import Path

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
LOGO_PATH = Path(HERE, "resources", "ascii-logo-80.txt")


@lru_cache
def get_logo() -> Text:
    """Load the text for the ASCII art.

    Ensure all lines same length and beginning with blank non-whitespace character.

    """
    with LOGO_PATH.open("r") as fp:
        lines = fp.read().split("\n")

    max_line_length = max(len(line) for line in lines)
    blank = "\N{ZERO WIDTH SPACE}"  # A blank non-whitespace character so Rich can center the logo
    padded_lines = [f"{blank}{line:{max_line_length}s}{blank}" for line in lines]

    logo_text = Text("\n".join(padded_lines))
    return logo_text


# class EnvironmentTree(TreeControl[Environment]):
#     has_focus = Reactive(False)
#
#     def __init__(self) -> None:
#         super().__init__("envs", data=Environment())
#
#     def on_focus(self) -> None:
#         self.has_focus = True
#
#     def on_blur(self) -> None:
#         self.has_focus = False
#
#     def render_node(self, node: TreeNode[Environment]) -> RenderableType:
#         return self.render_label(
#             node,
#             node.expanded,
#             node.is_cursor,
#             node.id == self.hover_node,
#             self.has_focus,
#         )
#
#     @lru_cache
#     def render_label(
#         self,
#         node: TreeNode[Environment],
#         expanded: bool,
#         is_cursor: bool,
#         is_hover: bool,
#         has_focus: bool,
#     ) -> RenderableType:
#         meta = {
#             "@click": f"click_label({node.id})",
#             "tree_node": node.id,
#             "cursor": node.is_cursor,
#         }
#
#         if not isinstance(node.label, str):
#             label = node.label
#         else:
#             label = Text(
#                 # if path is defined get a pretty name
#                 (node.data.rpath if is_hover else node.data.name or node.data.rpath)
#                 # if no path just reuse label
#                 or node.label,
#                 no_wrap=True,
#             )
#
#         if is_hover:
#             label.stylize("bold")
#
#         icon_label = (
#             Text(
#                 "\u25cf" if expanded else "\u25cb",
#                 no_wrap=True,
#             )
#             + " "
#             + label
#         )
#         icon_label.apply_meta(meta)
#         return icon_label
#
#     async def on_mount(self, event: Mount) -> None:
#         for env in list_environments():
#             await self.add(self.root.id, env.name or env.path, env)
#         await self.root.expand()


class EnvironmentList(Static):
    def compose(self) -> ComposeResult:
        """Generate a static list view of all conda environments"""
        items = []
        for env in list_environments():
            if env.name:
                label = f"[bold][green]{env.name}[/green][/bold] ({env.relative_path})"
            else:
                label = str(env.relative_path)
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

    # package_list: ScrollView
    # environment_list: ScrollView

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield Static(renderable=get_logo(), id="logo")
        yield EnvironmentList(classes="hidden", id="environment-list")

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
