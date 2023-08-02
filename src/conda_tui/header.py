from textual.reactive import Reactive
from textual.widgets import Header as _Header
from textual.widgets._header import HeaderClock
from textual.widgets._header import HeaderClockSpace
from textual.widgets._header import HeaderIcon as _HeaderIcon
from textual.widgets._header import HeaderTitle


class HeaderIcon(_HeaderIcon):
    """A custom header icon."""

    icon = Reactive("🐍")


class Header(_Header):
    """A custom header to display a custom snake icon."""

    def compose(self):
        yield HeaderIcon()
        yield HeaderTitle()
        yield HeaderClock() if self._show_clock else HeaderClockSpace()
