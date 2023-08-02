from functools import lru_cache
from pathlib import Path

from rich.console import RenderableType
from rich.text import Text
from textual.app import App
from textual.events import Mount
from textual.reactive import Reactive
from textual.widgets import ScrollView
from textual.widgets import TreeClick
from textual.widgets import TreeControl
from textual.widgets import TreeNode

from conda_tui.environment import Environment
from conda_tui.environment import list_environments
from conda_tui.footer import Footer
from conda_tui.header import Header
from conda_tui.package import list_packages_for_environment
from conda_tui.table import PackageTableWidget

HERE = Path(__file__).parent


@lru_cache
def get_logo() -> Text:
    """Load the text for the ASCII art.

    Ensure all lines same length and beginning with blank non-whitespace character.

    """
    with Path(HERE, "resources", "ascii-logo-80.txt").open("r") as fp:
        lines = fp.read().split("\n")

    max_line_length = max(len(line) for line in lines)
    blank = "\N{ZERO WIDTH SPACE}"  # A blank non-whitespace character so Rich can center the logo
    padded_lines = [f"{blank}{line:{max_line_length}s}{blank}" for line in lines]

    logo_text = Text("\n".join(padded_lines), style="#43b049", justify="center")
    return logo_text


class EnvironmentTree(TreeControl[Environment]):
    has_focus = Reactive(False)

    def __init__(self) -> None:
        super().__init__("envs", data=Environment())

    def on_focus(self) -> None:
        self.has_focus = True

    def on_blur(self) -> None:
        self.has_focus = False

    def render_node(self, node: TreeNode[Environment]) -> RenderableType:
        return self.render_label(
            node,
            node.expanded,
            node.is_cursor,
            node.id == self.hover_node,
            self.has_focus,
        )

    @lru_cache
    def render_label(
        self,
        node: TreeNode[Environment],
        expanded: bool,
        is_cursor: bool,
        is_hover: bool,
        has_focus: bool,
    ) -> RenderableType:
        meta = {
            "@click": f"click_label({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }

        if not isinstance(node.label, str):
            label = node.label
        else:
            label = Text(
                # if path is defined get a pretty name
                (node.data.rpath if is_hover else node.data.name or node.data.rpath)
                # if no path just reuse label
                or node.label,
                no_wrap=True,
            )

        if is_hover:
            label.stylize("bold")

        icon_label = (
            Text(
                "\u25cf" if expanded else "\u25cb",
                no_wrap=True,
            )
            + " "
            + label
        )
        icon_label.apply_meta(meta)
        return icon_label

    async def on_mount(self, event: Mount) -> None:
        for env in list_environments():
            await self.add(self.root.id, env.name or env.path, env)
        await self.root.expand()


class CondaTUI(App):
    """A hacked-together Conda Text User Interface (TUI)."""

    package_list: ScrollView
    environment_list: ScrollView

    async def on_load(self) -> None:
        """Sent before going in to application mode."""

        # Bind our basic keys
        await self.bind("h", "display_logo()", "Home")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode."""
        await self.view.dock(Header(style="white on #003764"), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        self.environment_list = ScrollView(EnvironmentTree())
        await self.view.dock(
            self.environment_list, edge="left", size=30, name="sidebar"
        )

        self.package_list = ScrollView(get_logo())
        await self.view.dock(self.package_list, edge="right")

    async def handle_tree_click(self, message: TreeClick[Environment]) -> None:
        """Display the package list if the environment exists."""
        if not message.node.data.path:
            return

        # if not message.node.loaded:
        await self.show_package_table(message.node)
        await message.node.expand()

    async def action_display_logo(self) -> None:
        """Display the logo when "H" is pressed."""
        await self.package_list.update(get_logo())

    async def show_package_table(self, node: TreeNode[Environment]) -> None:
        """Update the package list table based on selected environment."""
        packages = list_packages_for_environment(node.data)
        await self.package_list.update(PackageTableWidget(node.data, packages))


def run() -> None:
    """Run the application."""
    CondaTUI.run(title="conda TUI", log="textual.log")
