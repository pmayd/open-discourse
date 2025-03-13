from doit.tools import run_once

import open_discourse.steps.data.download_current_period as step2
import open_discourse.steps.data.download_MdB_data as step3
import open_discourse.steps.data.download_previous_periods as step1
from open_discourse.definitions import path

# Define the tasks for downloading the data.
# `name` is taken from the module name.
# `actions` is a list of functions to be executed.
#   The first action is the main function of the module.
#   The second action is to create a file that marks the task as done.
# `targets` is a list of files that are created by the task
#   and that can be used by downstream tasks as file dependency.
# `uptodate` is a list of functions that check if the task is up-to-date.
#   Because the download tasks have no dependencies, it is important to run them at least once.
TARGET_TASK1 = path.RAW_XML / "01_01.done"
TARGET_TASK2 = step2.OUTPUT_PATH / "01_02.done"
TARGET_TASK3 = path.MP_BASE_DATA / "01_03.done"

TASK_DEFINITION = {
    "step1": {
        "name": step1.__name__.split(".")[-1],
        "actions": [step1.main, f"touch {TARGET_TASK1}"],
        "targets": [TARGET_TASK1],
        "uptodate": [run_once],
    },
    "step2": {
        "name": step2.__name__.split(".")[-1],
        "actions": [step2.main, f"touch {TARGET_TASK2}"],
        "targets": [TARGET_TASK2],
        "uptodate": [run_once],
    },
    "step3": {
        "name": step3.__name__.split(".")[-1],
        "actions": [step3.main, f"touch {TARGET_TASK3}"],
        "targets": [TARGET_TASK3],
        "uptodate": [run_once],
    },
}


def task_01_download():
    """Download all election periods and the master data of all members of the parliament."""
    for _, task_definition in TASK_DEFINITION.items():
        yield task_definition
