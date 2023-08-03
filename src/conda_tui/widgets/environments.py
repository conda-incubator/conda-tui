from textual.app import ComposeResult
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView
from textual.widgets import Static

from conda_tui.environment import Environment
from conda_tui.environment import list_environments


class EnvironmentList(Static):
    environment_map: dict[str, Environment]

    def compose(self) -> ComposeResult:
        """Generate a static list view of all conda environments"""
        items = []
        self.environment_map = {}
        for i, env in enumerate(list_environments()):
            # TODO: Black/White should be based on hover
            if env.name:
                label = f"\N{BLACK CIRCLE} [bold][green]{env.name}[/green][/bold] ({env.relative_path})"
            else:
                label = f"\N{WHITE CIRCLE} {env.relative_path}"
            item_id = f"environment-{i}"
            self.environment_map[item_id] = env
            items.append(ListItem(Label(label), id=item_id))
        yield Static("Environment List", classes="center")
        yield ListView(*items)

    def on_list_view_selected(self, item: ListItem) -> None:
        """When we select a specific item on the list view, open the package list screen and
        set the environment reactive variable on that view."""
        screen = self.app.get_screen("package_list")
        screen.environment = self.environment_map[item.item.id]  # type: ignore
        self.app.push_screen(screen)
