import json
import tempfile
from pathlib import Path
from typing import Any
from typing import Optional

from rich.json import JSON
from textual.app import ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.screen import Screen as _Screen
from textual.widgets import DataTable
from textual.widgets import Footer
from textual.widgets import Log
from textual.widgets import Static

from conda_tui.environment import Environment
from conda_tui.environment import list_environments
from conda_tui.package import Package
from conda_tui.package import list_packages_for_environment
from conda_tui.widgets import Header
from conda_tui.widgets import Logo
from conda_tui.widgets import PackageUpdateProgress
from conda_tui.widgets.progress import ShellCommandProgress

HOME_TEXT = """\
Welcome to [cyan bold]conda-tui[/], your friendly helpful snake-chef.

To see a list of your 'conda' environments, please press [cyan bold]E[/].

"""


class Screen(_Screen):
    """A base screen class, used for wrapping a subclass with a header and footer."""

    header_text: str = reactive("conda-tui")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    def watch_header_text(self, value) -> None:
        self.app.title = value


class HomeScreen(Screen):
    """The home screen, displaying some helpful welcome text and the conda logo."""

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Logo(id="logo")
        yield Static(HOME_TEXT, markup=True)


class EnvironmentScreen(Screen):
    """A screen displaying a list of all conda environments on the system."""

    environments: list[Environment]

    def compose(self) -> ComposeResult:
        yield from super().compose()
        table = DataTable()
        table.cursor_type = "row"
        table.add_columns("Name", "Path")
        yield table

    def on_mount(self) -> None:
        self.environments = list_environments()
        table = self.query_one(DataTable)
        table.add_rows(
            [(f"[bold green]{env.name}[/]", env.prefix) for env in self.environments]
        )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """When we select a specific item on the list view, open the package list screen and
        set the environment reactive variable on that view."""
        screen = self.app.get_screen("package_list")
        screen.environment = self.environments[event.cursor_row]
        self.app.push_screen(screen)


class PackageListScreen(Screen):
    """A screen to display the packages installed into a specific environment."""

    environment = reactive[Optional[Environment]](None)
    packages: list[Package]

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("u", "update_package", "Update"),
        ("s", "show_available_updates", "Show Available Updates"),
    ]

    def compose(self) -> ComposeResult:
        yield from super().compose()
        assert self.environment is not None, "Shouldn't be possible"
        table = DataTable()
        table.cursor_type = "row"
        table.add_columns("Name", "Description", "", "Version", "Build", "Channel")
        self.packages = list_packages_for_environment(self.environment)
        for row_num, pkg in enumerate(self.packages):
            # TODO: Figure out a more dynamic way to do this
            description = pkg.description
            if len(description) > 80:
                description = description[: 80 - 3] + "..."

            table.add_row(
                pkg.name,
                description,
                pkg.status,
                pkg.version,
                pkg.build,
                pkg.schannel,
                key=pkg.name,
            )
        yield table

    def on_screen_resume(self) -> None:
        if self.environment.name:
            self.header_text = f"conda-tui: packages in {self.environment.name}"
        else:
            self.header_text = f"conda-tui: packages in {self.environment.prefix}"

        self.run_worker(self.refresh_package_statuses)

    async def refresh_package_statuses(self):
        """Call conda in the background to get update results, and update the statuses in the table."""
        import asyncio
        import subprocess

        if self.environment.name:
            env_args = ["-n", self.environment.name]
        else:
            env_args = ["-p", str(self.environment.prefix)]
        command = ["conda", "update", *env_args, "--all", "--dry-run", "--json"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir, "tmp.json")
            with tmp_path.open("w") as fp:
                process = subprocess.Popen(command, stdout=fp, stderr=fp)
                while process.poll() is None:
                    await asyncio.sleep(0.1)

            with tmp_path.open("r") as fp:
                try:
                    data = json.load(fp)
                except json.JSONDecodeError:
                    data = {}

        fetch_names = {
            pkg["name"]: pkg["version"]
            for pkg in data.get("actions", {}).get("FETCH", [])
        }

        table = self.query_one(DataTable)
        for row_num, package in enumerate(self.packages):
            if package.name in fetch_names:
                package.update_available = True
                table.update_cell_at(
                    (row_num, 3),
                    f"{package.version} \N{RIGHTWARDS ARROW} {fetch_names[package.name]}",
                )
            else:
                package.update_available = False
            table.update_cell_at((row_num, 2), package.status)

    def action_go_back(self) -> None:
        self.dismiss()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Push a new package detail screen when a package is selected."""
        self.app.push_screen(
            PackageDetailScreen(package=self.packages[event.cursor_row])
        )

    def action_update_package(self):
        """Launch a new screen to display package update progress."""
        table = self.query_one(DataTable)
        row_num = table.cursor_row
        package = self.packages[row_num]

        def update_package_status(was_success: bool):
            if was_success:
                table.update_cell_at((row_num, 2), package.status)

        self.app.push_screen(
            PackageUpdateScreen(package=package), update_package_status
        )

    def action_show_available_updates(self) -> None:
        if self.environment.name:
            env_args = ["-n", self.environment.name]
        else:
            env_args = ["-p", str(self.environment.prefix)]
        screen = ShellCommandScreen(
            ["conda", "update", *env_args, "--all", "--dry-run"]
        )
        self.app.push_screen(screen)


class PackageUpdateScreen(Screen):
    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, *args: Any, package: Package, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._package = package

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Static(f"Updating package [cyan bold]`{self._package.name}`[/cyan bold]")
        yield Static("[red bold]TODO[/red bold]: Hook this up to actual download")
        yield PackageUpdateProgress(package=self._package)

    def action_go_back(self):
        self.dismiss()


class ShellCommandScreen(Screen):
    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, command: list[str], **kwargs: Any):
        super().__init__(**kwargs)
        self._command = command

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield ShellCommandProgress()
        yield Log(highlight=True, id="shell-command-log")

    def on_screen_resume(self) -> None:
        log = self.query_one("#shell-command-log")
        log.clear()
        progress = self.query_one(ShellCommandProgress)
        self.run_worker(progress.run_command(self._command, log=log))

    def action_go_back(self):
        self.dismiss()


class PackageDetailScreen(Screen):
    """A screen to display the details of a package."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, *args: Any, package: Package, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._package = package

    def compose(self) -> ComposeResult:
        # TODO: This is just a simple JSON dump, should be nicer.
        yield from super().compose()
        yield Grid(
            Static(
                f"Package details for [cyan bold]`{self._package.name}`[/cyan bold]:"
            ),
            Static(JSON(json.dumps(self._package.dist_fields_dump()))),
            id="package-details",
        )

    def action_go_back(self):
        self.dismiss()
