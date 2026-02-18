"""Kachi is a simple tool for backing up valuable files."""

import logging

__version__ = "0.1.14"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output matching installation script format."""

    # ANSI color codes matching install.sh
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    NC = "\033[0m"  # No Color

    COLORS = {
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: RED,
    }

    def format(self, record):
        """Format log record with colors."""
        color = self.COLORS.get(record.levelno, self.NC)
        record.levelname = f"{color}[{record.levelname}]{self.NC}"
        return super().format(record)


# Configure logging with colored formatter
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter("%(levelname)s %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
logger = logging.getLogger(__name__)
