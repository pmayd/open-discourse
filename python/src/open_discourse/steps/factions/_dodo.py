import open_discourse.steps.factions.add_abbreviations_and_ids as step2
import open_discourse.steps.factions.create as step1
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
TARGET_TASK1 = path.FACTIONS_STAGE_01 / "03_01.done"
TARGET_TASK2 = path.FINAL / "03_02.done"

TASK_DEFINITION = {
    "step1": {
        "name": step1.__name__.split(".")[-1],
        "actions": [step1.main, f"touch {TARGET_TASK1}"],
        "targets": [TARGET_TASK1],
        "task_dep": ["02_preprocessing:extract_mps_from_mp_base_data"],
        "file_dep": [preprocessing_task.TARGET_TASK4],
    },
    "step2": {
        "name": step2.__name__.split(".")[-1],
        "actions": [step2.main, f"touch {TARGET_TASK2}"],
        "targets": [TARGET_TASK2],
        "task_dep": ["03_factions:create"],
        "file_dep": [TARGET_TASK1],
    },
}


def task_03_factions():
    """Preprocess/split the XML data."""
    for _, task_definition in TASK_DEFINITION.items():
        yield task_definition
