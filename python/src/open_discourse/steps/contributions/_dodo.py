import open_discourse.steps.contributions.clean as step2
import open_discourse.steps.contributions.extract as step1
import open_discourse.steps.contributions.match as step3
import open_discourse.steps.data._dodo as download_task
import open_discourse.steps.factions._dodo as factions_task
import open_discourse.steps.politicians._dodo as politicians_task
import open_discourse.steps.preprocessing._dodo as preprocessing_task
import open_discourse.steps.speech_content._dodo as speech_content_task
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
    path.SPEECH_CONTENT_STAGE_04 / "07_01.done",
    path.CONTRIBUTIONS_EXTENDED_STAGE_01 / "07_01.done",
    path.FINAL / "07_01.done",
]
TARGET_TASK2 = path.CONTRIBUTIONS_EXTENDED_STAGE_02 / "07_02.done"
TARGET_TASK3 = path.CONTRIBUTIONS_EXTENDED_STAGE_03 / "07_03.done"

TASK_DEFINITION = {
    "step1": {
        "name": step1.__name__.split(".")[-1],
        "actions": [step1.main] + [f"touch {target}" for target in TARGET_TASK1],
        "targets": TARGET_TASK1,
        "task_dep": [
            "03_factions:add_abbreviations_and_ids",
            "05_speech_content:match_names",
        ],
        "file_dep": [factions_task.TARGET_TASK2, speech_content_task.TARGET_TASK3],
    },
    "step2": {
        "name": step2.__name__.split(".")[-1],
        "actions": [step2.main, f"touch {TARGET_TASK2}"],
        "targets": [TARGET_TASK2],
        "task_dep": [
            "03_factions:add_abbreviations_and_ids",
            "07_contributions:extract",
        ],
        "file_dep": [factions_task.TARGET_TASK2] + TARGET_TASK1,
    },
    "step3": {
        "name": step3.__name__.split(".")[-1],
        "actions": [step3.main, f"touch {TARGET_TASK3}"],
        "targets": [TARGET_TASK3],
        "task_dep": ["03_factions:add_abbreviations_and_ids", "04_politicians:merge"],
        "file_dep": [factions_task.TARGET_TASK2, politicians_task.TARGET_TASK3],
    },
}


def task_07_contributions():
    """Preprocess/split the XML data."""
    for _, task_definition in TASK_DEFINITION.items():
        yield task_definition
