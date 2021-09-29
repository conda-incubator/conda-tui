from pathlib import Path

from rich.table import Table
from rich.text import Text
from textual.app import App
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import ScrollView

from conda_tui.environment import list_environments

HERE = Path(__file__).parent

# Load the text for the ASCII art, ensure all lines same length
with Path(HERE, "resources", "ascii-logo-80.txt").open("r") as fp:
    LOGO_TEXT = fp.read()


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

        table = Table("Name", "Path", title="Environments")
        for env in list_environments():
            table.add_row(env.name, env.path)

        environment_list = ScrollView(table)

        # Display the package list
        # TODO: Should toggle between logo and list when environment is selected
        text = Text(LOGO_TEXT, style="green", justify="left")
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
