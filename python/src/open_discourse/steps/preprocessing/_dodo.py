import open_discourse.steps.data._dodo as download_task
import open_discourse.steps.preprocessing.create_electoral_terms as step5
import open_discourse.steps.preprocessing.extract_mps_from_mp_base_data as step4
import open_discourse.steps.preprocessing.split_xml as step2
import open_discourse.steps.preprocessing.split_xml_electoral_term_1_and_2 as step1
import open_discourse.steps.preprocessing.split_xml_electoral_term_20 as step3
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
TARGET_TASK1 = path.RAW_TXT / "02_01.done"
TARGET_TASK2 = path.RAW_TXT / "02_02.done"
TARGET_TASK3 = step3.OUTPUT_PATH / "02_03.done"
TARGET_TASK4 = path.POLITICIANS_STAGE_01 / "02_04.done"
TARGET_TASK5 = path.FINAL / "02_05.done"

TASK_DEFINITION = {
    "step1": {
        "name": step1.__name__.split(".")[-1],
        "actions": [step1.main, f"touch {TARGET_TASK1}"],
        "targets": [TARGET_TASK1],
        "task_dep": ["01_download:download_previous_periods"],
        "file_dep": [download_task.TARGET_TASK1],
    },
    "step2": {
        "name": step2.__name__.split(".")[-1],
        "actions": [step2.main, f"touch {TARGET_TASK2}"],
        "targets": [TARGET_TASK2],
        "task_dep": ["01_download:download_previous_periods"],
        "file_dep": [download_task.TARGET_TASK1],
    },
    "step3": {
        "name": step3.__name__.split(".")[-1],
        "actions": [step3.main, f"touch {TARGET_TASK3}"],
        "targets": [TARGET_TASK3],
        "task_dep": ["01_download:download_current_period"],
        "file_dep": [download_task.TARGET_TASK2],
    },
    "step4": {
        "name": step4.__name__.split(".")[-1],
        "actions": [step4.main, f"touch {TARGET_TASK4}"],
        "targets": [TARGET_TASK4],
        "task_dep": ["01_download:download_MdB_data"],
        "file_dep": [download_task.TARGET_TASK3],
    },
    "step5": {
        "name": step5.__name__.split(".")[-1],
        "actions": [step5.main, f"touch {TARGET_TASK5}"],
        "targets": [TARGET_TASK5],
    },
}


def task_02_preprocessing():
    """Preprocess/split the XML data."""
    for _, task_definition in TASK_DEFINITION.items():
        yield task_definition
