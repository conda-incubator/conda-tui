from pathlib import Path

from textual.app import App

from conda_tui.screens import EnvironmentScreen
from conda_tui.screens import HomeScreen
from conda_tui.screens import PackageListScreen
from conda_tui.screens import ShellCommandScreen


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
        ("?", "run_command(['conda', '-h'])", "Help"),
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """When we start up, push the home screen.

        This allows us to use switch_screen to switch between the various views without
        having an infinitely-growing screen stack.

        """
        self.push_screen("home")

    def action_run_command(self, command: list[str]) -> None:
        screen = ShellCommandScreen(command)
        self.push_screen(screen)


def run() -> None:
    """Run the application."""
    CondaTUI().run()
