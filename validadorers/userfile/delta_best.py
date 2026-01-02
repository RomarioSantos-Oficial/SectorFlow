

from __future__ import annotations

import csv
import logging

from ..const_file import FileExt
from ..validator import invalid_save_name, valid_delta_set

logger = logging.getLogger(__name__)


def load_delta_best_file(
    filepath: str, filename: str, defaults: tuple, extension: str = FileExt.CSV
) -> tuple[tuple, float]:
    """Load delta best file (*.csv)"""
    try:
        with open(f"{filepath}{filename}{extension}", newline="", encoding="utf-8") as csvfile:
            data_reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            temp_list = tuple(tuple(data) for data in data_reader)
        # Validate data
        bestlist = valid_delta_set(temp_list)
        laptime_best = bestlist[-1][1]
        return bestlist, laptime_best
    except FileNotFoundError:
        logger.info("MISSING: delta best (%s) data", extension)
    except (IndexError, ValueError, TypeError):
        logger.info("MISSING: invalid delta best (%s) data", extension)
    return defaults


def save_delta_best_file(
    filepath: str, filename: str, dataset: tuple, extension: str = FileExt.CSV
) -> None:
    """Save delta best file (*.csv)"""
    if len(dataset) < 10 or invalid_save_name(filename):
        return
    with open(f"{filepath}{filename}{extension}", "w", newline="", encoding="utf-8") as csvfile:
        data_writer = csv.writer(csvfile)
        data_writer.writerows(dataset)
        logger.info("USERDATA: %s%s saved", filename, extension)
