import open_discourse.steps.electoral_term_20.extract as step1
import open_discourse.steps.factions._dodo as factions_task
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
TARGET_TASK1 = [
    step1.ELECTORAL_TERM_20_OUTPUT / "06_01.done",
    path.FINAL / "06_01.done",
    path.CONTRIBUTIONS_EXTENDED_STAGE_01 / "06_01.done",
]

TASK_DEFINITION = {
    "step1": {
        "name": step1.__name__.split(".")[-1],
        "actions": [step1.main] + [f"touch {target}" for target in TARGET_TASK1],
        "targets": TARGET_TASK1,
        "task_dep": [
            "02_preprocessing:split_xml_electoral_term_20",
            "03_factions:add_abbreviations_and_ids",
        ],
        "file_dep": [preprocessing_task.TARGET_TASK3, factions_task.TARGET_TASK2],
    },
}


def task_06_electoral_term_20():
    """Preprocess/split the XML data."""
    for _, task_definition in TASK_DEFINITION.items():
        yield task_definition
