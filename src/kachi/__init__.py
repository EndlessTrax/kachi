"""Kachi is a simple tool for backing up valuable files."""

import logging

from rich.logging import RichHandler
from rich.text import Text

__version__ = "0.2.0"


class KachiLogHandler(RichHandler):
    """Custom Rich log handler with bracketed level format matching install scripts."""

    def get_level_text(self, record):
        """Format the log level as [LEVEL] with Rich styling.

        Args:
            record: The log record to format.

        Returns:
            A Rich Text object with the formatted level string.
        """
        level = record.levelname
        level_text = Text(f"[{level}]")
        level_text.stylize(f"logging.level.{level.lower()}")
        return level_text


# Configure logging with Rich handler
handler = KachiLogHandler(
    show_time=False,
    show_path=False,
    markup=True,
    rich_tracebacks=True,
)
logging.basicConfig(
    level=logging.INFO, handlers=[handler], format="%(message)s", force=True
)
logger = logging.getLogger(__name__)
