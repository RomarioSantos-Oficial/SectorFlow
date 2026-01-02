

from __future__ import annotations

import csv
import logging

from ..validator import invalid_save_name, valid_delta_set

logger = logging.getLogger(__name__)


def load_fuel_delta_file(
    filepath: str, filename: str, extension: str, defaults: tuple
) -> tuple[tuple, float, float]:
    """Load fuel/energy delta file (*.fuel, *.energy)"""
    try:
        with open(f"{filepath}{filename}{extension}", newline="", encoding="utf-8") as csvfile:
            data_reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            temp_list = tuple(tuple(data) for data in data_reader)
        # Validate data
        lastlist = valid_delta_set(temp_list)
        used_last = lastlist[-1][1]
        laptime_last = lastlist[-1][2]
        return lastlist, used_last, laptime_last
    except FileNotFoundError:
        logger.info("MISSING: consumption delta (%s) data", extension)
    except (IndexError, ValueError, TypeError):
        logger.info("MISSING: invalid consumption delta (%s) data", extension)
    return defaults


def save_fuel_delta_file(
    filepath: str, filename: str, extension: str, dataset: tuple
) -> None:
    """Save fuel/energy delta file (*.fuel, *.energy)"""
    if len(dataset) < 10 or invalid_save_name(filename):
        return
    with open(f"{filepath}{filename}{extension}", "w", newline="", encoding="utf-8") as csvfile:
        data_writer = csv.writer(csvfile)
        data_writer.writerows(dataset)
        logger.info("USERDATA: %s%s saved", filename, extension)
