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


# Task function for backward compatibility
def task_04_politicians():
    """Processes politician data by merging MP information with faction IDs and scraped data."""

    # Sub-tasks to match the old naming convention expected by other tasks
    yield {
        "name": "scrape_mgs",
        "actions": [
            # This is a wrapper that calls the new task
            "python -m open_discourse.steps.politicians.scrape_mgs"
        ],
        "targets": [TARGET_TASK2],
        "verbosity": 2,
    }

    yield {
        "name": "add_faction_id",
        "actions": ["python -m open_discourse.steps.politicians.add_faction_id_to_mps"],
        "file_dep": [TARGET_TASK2],
        "targets": [TARGET_TASK1],
        "verbosity": 2,
    }

    yield {
        "name": "merge",
        "actions": ["python -m open_discourse.steps.politicians.merge"],
        "file_dep": [TARGET_TASK1, TARGET_TASK2],
        "targets": [TARGET_TASK3],
        "verbosity": 2,
    }
