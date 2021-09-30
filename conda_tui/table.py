import json
from pathlib import Path
from typing import List

from rich.console import RenderableType
from rich.table import Table
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from conda_tui.package import Package


class PackageTableWidget(Widget):
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
            "Description",
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

            with Path(pkg.extracted_package_dir, "info", "about.json").open("r") as fh:
                description = json.load(fh).get("summary", "")

            texts = {
                "name": Text(pkg.name, style=style),
                "description": Text(description, style=style),
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
