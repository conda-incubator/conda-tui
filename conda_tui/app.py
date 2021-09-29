from pathlib import Path

from rich.console import RenderableType
from rich.text import Text
from textual.app import App
from textual.events import Mount
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import ScrollView
from textual.widgets import TreeControl
from textual.widgets import TreeNode

from conda_tui.environment import Environment
from conda_tui.environment import get_envs

HERE = Path(__file__).parent


def get_logo() -> str:
    """Load the text for the ASCII art.

    Ensure all lines same length and beginning with blank non-whitespace character.

    """
    with Path(HERE, "resources", "ascii-logo-80.txt").open("r") as fp:
        lines = [line.rstrip() for line in fp.readlines()]

    max_line_length = max(len(line) for line in lines)
    blank = "\N{ZERO WIDTH SPACE}"  # A blank non-whitespace character so Rich can center the logo
    padded_lines = [f"{blank}{line:{max_line_length}s}{blank}" for line in lines]

    logo_text = "\n".join(padded_lines)
    return logo_text


class EnvironmentTree(TreeControl[Environment]):
    def __init__(self) -> None:
        super().__init__("envs", data=Environment())

    def render_node(self, node: TreeNode[Environment]) -> RenderableType:
        if not isinstance(node.label, str):
            label = node.label
        else:
            label = Text(
                # if path is defined get a pretty name
                (
                    node.data.rpath
                    if node.id == self.hover_node
                    else node.data.name or node.data.rpath
                )
                # if no path just reuse label
                or node.label,
                no_wrap=True,
            )
        if node.id == self.hover_node:
            label.stylize("bold")
        label.apply_meta({"@click": f"click_label({node.id})", "tree_node": node.id})
        return label

    async def on_mount(self, event: Mount) -> None:
        for env in get_envs():
            await self.add(self.root.id, env.name or env.path, env)
        await self.root.expand()


class CondaTUI(App):
    """A hacked-together Conda Text User Interface (TUI)."""

    async def on_load(self) -> None:
        """Sent before going in to application mode."""

        # Bind our basic keys
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

        environment_list = EnvironmentTree()

        # Display the package list
        # TODO: Should toggle between logo and list when environment is selected
        text = Text(get_logo(), style="green", justify="center")
        package_list = ScrollView(text)

        grid.place(
            header=Header(),
            env_list=environment_list,
            package_list=package_list,
            footer=Footer(),
        )


def run() -> None:
    """Run the application."""
    CondaTUI.run(title="conda TUI", log="textual.log")
