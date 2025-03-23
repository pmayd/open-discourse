"""
Task definitions for the politicians processing steps.

This module defined the politicians processing tasks for the old doit system.
It's kept for backward compatibility.
"""

from open_discourse.definitions import path

# Define targets for backward compatibility
TARGET_TASK1 = path.POLITICIANS_STAGE_02 / "04_01.done"
TARGET_TASK2 = path.POLITICIANS_STAGE_01 / "04_02.done"
TARGET_TASK3 = path.DATA_FINAL / "04_03.done"

# Empty task function for compatibility
def task_04_politicians():
    """Processes politician data by merging MP information with faction IDs and scraped data."""
    return []