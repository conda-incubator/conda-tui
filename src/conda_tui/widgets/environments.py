from textual.app import ComposeResult
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView
from textual.widgets import Static

from conda_tui.environment import list_environments


class EnvironmentList(Static):
    def compose(self) -> ComposeResult:
        """Generate a static list view of all conda environments"""
        items = []
        for env in list_environments():
            # TODO: Black/White should be based on hover
            if env.name:
                label = f"\N{BLACK CIRCLE} [bold][green]{env.name}[/green][/bold] ({env.relative_path})"
            else:
                label = f"\N{WHITE CIRCLE} {env.relative_path}"
            items.append(ListItem(Label(label)))
        yield Static("Environment List", classes="center")
        yield ListView(*items)
