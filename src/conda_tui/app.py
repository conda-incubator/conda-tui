import argparse
import sys
from pathlib import Path
from typing import Optional

import conda.plugins
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
        ("i", "run_command(['conda', 'info'])", "Info"),
        ("q", "quit", "Quit"),
        ("?", "run_command(['conda', '-h'])", "Help"),
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


def run(argv: Optional[list[str]] = None) -> None:
    """Run the application."""
    # We have to consider multiple ways of launching the application:
    #   * conda tui
    #   * conda-tui
    #   * python -m conda_tui
    # When we use `conda tui`, this function is called with prefix args removed.
    # For the other two ways, we have to remove the first system argument
    # to remove the root executable.
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser("conda tui")
    parser.add_argument("--no-dark", action="store_true", help="Disable dark mode")
    args = parser.parse_args(argv)

    app = CondaTUI()
    app.dark = not args.no_dark
    app.run()


@conda.plugins.hookimpl
def conda_subcommands():
    yield conda.plugins.CondaSubcommand(
        name="tui",
        summary="A Terminal User Interface for conda",
        action=run,
        # configure_parser=config_parser,
    )
