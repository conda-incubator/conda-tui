from pathlib import Path

from rich.text import Text
from textual.app import App
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import ScrollView

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

        # Create our widgets
        text = Text(LOGO_TEXT, style="green", justify="left")
        self.body = ScrollView(text)

        # Dock our widgets
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        # Dock the logo body view
        await self.view.dock(self.body, edge="top")


def run() -> None:
    """Run the application."""
    CondaTUI.run(title="conda TUI", log="textual.log")
