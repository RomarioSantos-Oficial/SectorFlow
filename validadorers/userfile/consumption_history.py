

from __future__ import annotations

import csv
import logging

from ..const_file import FileExt
from ..module_info import ConsumptionDataSet
from ..validator import dict_value_type, invalid_save_name

logger = logging.getLogger(__name__)


def load_consumption_history_file(
    filepath: str, filename: str, extension: str = FileExt.CONSUMPTION
) -> tuple[ConsumptionDataSet, ...]:
    """Load fuel/energy consumption history file (*.consumption)"""
    try:
        with open(f"{filepath}{filename}{extension}", newline="", encoding="utf-8") as csvfile:
            data_reader = csv.DictReader(csvfile, restval="", restkey="unknown")
            default_data = ConsumptionDataSet._field_defaults
            dataset = tuple(
                ConsumptionDataSet(**dict_value_type(data, default_data))
                for data in data_reader
            )
            if not dataset:
                raise ValueError
        return dataset
    except FileNotFoundError:
        logger.info("MISSING: consumption history (%s) data", extension)
    except (IndexError, KeyError, ValueError, TypeError):
        logger.info("MISSING: invalid consumption history (%s) data", extension)
    return (ConsumptionDataSet(),)


def save_consumption_history_file(
    dataset: tuple, filepath: str, filename: str, extension: str = FileExt.CONSUMPTION
) -> None:
    """Save fuel/energy consumption history file (*.consumption)"""
    if len(dataset) < 2 or invalid_save_name(filename):
        return
    with open(f"{filepath}{filename}{extension}", "w", newline="", encoding="utf-8") as csvfile:
        data_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        data_writer.writerow(ConsumptionDataSet._fields)  # write field name as column header
        data_writer.writerows(dataset)
        logger.info("USERDATA: %s%s saved", filename, extension)
