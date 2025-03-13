import open_discourse.steps.contributions._dodo as contributions_task
import open_discourse.steps.data._dodo as download_task
import open_discourse.steps.database.concat as step1
import open_discourse.steps.database.upload as step2
import open_discourse.steps.electoral_term_20._dodo as electoral_term_20_task
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
TARGET_TASK1 = path.FINAL / "08_01.done"
TARGET_TASK2 = path.FINAL / "08_02.done"

TASK_DEFINITION = {
    "step1": {
        "name": step1.__name__.split(".")[-1],
        "actions": [step1.main, f"touch {TARGET_TASK1}"],
        "targets": [TARGET_TASK1],
        "task_dep": [
            "01_download:download_previous_periods",
            "06_electoral_term_20",
            "07_contributions:extract",
            "07_contributions:match",
        ],
        "file_dep": [
            download_task.TARGET_TASK1,
            electoral_term_20_task.TARGET_TASK1[0],
            contributions_task.TARGET_TASK1[0],
            contributions_task.TARGET_TASK3,
        ],
    },
    "step2": {
        "name": step2.__name__.split(".")[-1],
        "actions": [step2.main, f"touch {TARGET_TASK2}"],
        "targets": [TARGET_TASK2],
        "task_dep": ["08_upload:concat"],
        "file_dep": [TARGET_TASK1],
    },
}


def task_08_upload():
    """Preprocess/split the XML data."""
    for _, task_definition in TASK_DEFINITION.items():
        yield task_definition
