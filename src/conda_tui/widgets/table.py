from functools import cached_property
from typing import Optional

from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from conda_tui.environment import Environment
from conda_tui.package import list_packages_for_environment


class PackageTableWidget(Widget):
    """A table widget allowing custom rendering of cell contents when hovering and clicking."""

    hover_row = reactive(None)

    def __init__(self, env: Environment):
        super().__init__()
        self._env = env
        self._packages = list_packages_for_environment(env)

    @cached_property
    def title(self) -> str:
        if self._env.name:
            return f"[bold][green]{self._env.name}[/green][/bold] ({self._env.relative_path})"
        else:
            return f"{self._env.relative_path}"

    def render(self) -> RenderableType:
        """Render the package table."""
        # TODO: Consider rendering each row individually, as this probably won't scale.
        self.log("Rendering table")
        table = Table(
            "Name",
            "Description",
            "Version",
            "Build",
            "Channel",
            title=self.title,
            expand=True,
        )
        for row_num, pkg in enumerate(self._packages):
            style: Optional[Style] = None
            if self.hover_row == row_num:
                style = Style(reverse=True, bold=True)

            texts = {
                "name": Text(pkg.name),
                "description": Text(pkg.description),
                "version": pkg.status,
                "build": Text(pkg.build),
                "schannel": Text(pkg.schannel),
            }
            table.add_row(*texts.values(), style=style)

            # Embed the row number and column key as meta-style attributes
            # Can be pulled out by `on_mouse_move`
            for key, text in texts.items():
                if not isinstance(text, Text):
                    continue
                text.apply_meta(
                    {
                        "@click": f"click_row({row_num}, '{key}')",
                        "row_num": row_num,
                        "col_name": key,
                    }
                )
        return table

    # async def on_mount(self) -> None:
    #     self.set_interval(1.0, callback=self.refresh)
    #
    # async def on_mouse_move(self, event: events.MouseMove) -> None:
    #     self.log(f"Mouse move, row = {event.style.meta.get('row_num')}")
    #     self.hover_row = event.style.meta.get("row_num")
    #
    # async def action_click_row(self, row_id: int, col_name: str) -> None:
    #     self.log(f"Clicked row: {row_id}, column: {col_name}")
    #
    #     timer = self.set_interval(1.0, callback=self._packages[row_id].increment)
    #     self._packages[row_id].update(self.console, timer)
