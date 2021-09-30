from functools import lru_cache
from pathlib import Path
from typing import List

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual import events
from textual.app import App
from textual.events import Mount
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import ScrollView
from textual.widgets import TreeClick
from textual.widgets import TreeControl
from textual.widgets import TreeNode

from conda_tui.environment import Environment
from conda_tui.environment import list_environments
from conda_tui.package import list_packages_for_environment
from conda_tui.package import Package

HERE = Path(__file__).parent


@lru_cache()
def get_logo() -> Text:
    """Load the text for the ASCII art.

    Ensure all lines same length and beginning with blank non-whitespace character.

    """
    with Path(HERE, "resources", "ascii-logo-80.txt").open("r") as fp:
        lines = [line.rstrip() for line in fp.readlines()]

    max_line_length = max(len(line) for line in lines)
    blank = "\N{ZERO WIDTH SPACE}"  # A blank non-whitespace character so Rich can center the logo
    padded_lines = [f"{blank}{line:{max_line_length}s}{blank}" for line in lines]

    logo_text = Text("\n".join(padded_lines), style="green", justify="center")
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


class PackageTableControl(Widget):
    """A table widget allowing custom rendering of cell contents when hovering and clicking."""

    hover_row = Reactive(None)

    def __init__(self, data: List[Package], *, name: str = None):
        super().__init__(name=name)
        self._data = data

    def render(self) -> RenderableType:
        """Render the package table."""
        self.log("Rendering table")
        table = Table(
            "Name",
            "Version",
            "Build",
            "Features",
            "Channel",
            title="Packages",
            expand=True,
        )
        for row_num, pkg in enumerate(self._data):
            style = ""
            if self.hover_row == row_num:
                style = "bold red"
            texts = {
                "name": Text(pkg.name, style=style),
                "version": Text(pkg.version, style=style),
                "build": Text(pkg.build, style=style),
                "features": Text(", ".join(pkg.get("features", ())), style=style),
                "schannel": Text(pkg.schannel, style=style),
            }
            table.add_row(*texts.values())

            # Embed the row number and column key as meta-style attributes
            # Can be pulled out by `on_mouse_move`
            for key, text in texts.items():
                text.apply_meta(
                    {
                        "@click": f"click_row({row_num}, '{key}')",
                        "row_num": row_num,
                        "col_name": key,
                    }
                )
        return table

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        self.log(f"Mouse move, row = {event.style.meta.get('row_num')}")
        self.hover_row = event.style.meta.get("row_num")

    async def action_click_row(self, row_id: int, col_name: str) -> None:
        self.log(f"Clicked row: {row_id}, column: {col_name}")


class CondaTUI(App):
    """A hacked-together Conda Text User Interface (TUI)."""

    package_list: ScrollView

    async def on_load(self) -> None:
        """Sent before going in to application mode."""

        # Bind our basic keys
        await self.bind("h", "display_logo()", "Home")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Call after terminal goes in to application mode"""

        grid = await self.view.dock_grid()

        grid.add_column(fraction=1, name="left", min_size=20)
        grid.add_column(fraction=3, name="right")

        # TODO: I can't seem to get the main row to expand to full-screen when I set max_size
        #       of header and footer. Maybe a Textual bug we can fix and PR?
        #       To reproduce, remove 'min_size' argument from the main row.
        grid.add_row(name="header", max_size=3)
        grid.add_row(name="main", min_size=50)
        grid.add_row(name="footer", max_size=1)

        grid.add_areas(
            header="left-start|right-end,header",
            env_list="left,main",
            package_list="right,main",
            footer="left-start|right-end,footer",
        )

        # Display the logo in the package list pane
        self.package_list = ScrollView(get_logo())

        grid.place(
            header=Header(),
            env_list=EnvironmentTree(),
            package_list=self.package_list,
            footer=Footer(),
        )

    async def handle_tree_click(self, message: TreeClick[Environment]) -> None:
        if not message.node.data.path:
            return

        # if not message.node.loaded:
        await self.load_packages(message.node)
        await message.node.expand()

    async def action_display_logo(self) -> None:
        """Display the logo when "H" is pressed."""
        await self.package_list.update(get_logo())

    async def load_packages(self, node: TreeNode[Environment]) -> None:
        packages = list_packages_for_environment(node.data)
        await self.package_list.update(PackageTableControl(packages))


def run() -> None:
    """Run the application."""
    CondaTUI.run(title="conda TUI", log="textual.log")
