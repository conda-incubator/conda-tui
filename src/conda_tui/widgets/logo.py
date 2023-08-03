from functools import cache
from pathlib import Path
from typing import Any

from rich.text import Text
from textual.widgets import Static

LOGO_PATH = Path(__file__).parents[1] / "resources" / "ascii-logo-80.txt"


class Logo(Static):
    """A static display of the conda logo"""

    def __init__(self, **kwargs: Any):
        super().__init__(renderable=self.get_logo(), **kwargs)

    @staticmethod
    @cache
    def get_logo() -> Text:
        """Load the text for the ASCII art.

        Ensure all lines same length and beginning with blank non-whitespace character.

        """
        with LOGO_PATH.open("r") as fp:
            lines = fp.read().split("\n")

        max_line_length = max(len(line) for line in lines)
        blank = "\N{ZERO WIDTH SPACE}"  # A blank non-whitespace character so Rich can center the logo
        padded_lines = [f"{blank}{line:{max_line_length}s}{blank}" for line in lines]

        logo_text = Text("\n".join(padded_lines))
        return logo_text
