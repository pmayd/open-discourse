import open_discourse.steps.factions._dodo as factions_task
import open_discourse.steps.politicians.add_faction_id_to_mps as step1
import open_discourse.steps.politicians.merge as step3
import open_discourse.steps.politicians.scrape_mgs as step2
import open_discourse.steps.preprocessing._dodo as preprocessing_task
from open_discourse.definitions import path

# Define the tasks for downloading the data.
# `name` is taken from the module name.
# `actions` is a list of functions to be executed.
#   The first action is the main function of the module.
#   The second action is to create a file that marks the task as done.
# `targets` is a list of files that are created by the task
#   and that can be used by downstream tasks as file dependency.
# `uptodate` is a list of functions that check if the task is up-to-date.
# `task_dep` is a list of tasks that have to run before this task.
# `file_dep` is a list of files that are required for this task.
TARGET_TASK1 = path.POLITICIANS_STAGE_02 / "04_01.done"
TARGET_TASK2 = path.POLITICIANS_STAGE_01 / "04_02.done"
TARGET_TASK3 = path.FINAL / "04_03.done"

TASK_DEFINITION = {
    "step1": {
        "name": step1.__name__.split(".")[-1],
        "actions": [step1.main, f"touch {TARGET_TASK1}"],
        "targets": [TARGET_TASK1],
        "task_dep": [
            "02_preprocessing:extract_mps_from_mp_base_data",
            "03_factions:add_abbreviations_and_ids",
        ],
        "file_dep": [preprocessing_task.TARGET_TASK4, factions_task.TARGET_TASK2],
    },
    "step2": {
        "name": step2.__name__.split(".")[-1],
        "actions": [step2.main, f"touch {TARGET_TASK2}"],
        "targets": [TARGET_TASK2],
        "task_dep": [],
        "file_dep": [],
    },
    "step3": {
        "name": step3.__name__.split(".")[-1],
        "actions": [step3.main, f"touch {TARGET_TASK3}"],
        "targets": [TARGET_TASK3],
        "task_dep": [
            "03_factions:add_abbreviations_and_ids",
            "04_politicians:add_faction_id_to_mps",
            "04_politicians:scrape_mgs",
        ],
        "file_dep": [factions_task.TARGET_TASK2, TARGET_TASK1, TARGET_TASK2],
    },
}


def task_04_politicians():
    """Preprocess/split the XML data."""
    for _, task_definition in TASK_DEFINITION.items():
        yield task_definition
