"""Kachi is a simple tool for backing up valuable files."""

import logging

__version__ = "0.1.8"

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
