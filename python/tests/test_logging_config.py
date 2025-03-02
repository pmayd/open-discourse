import logging
import os
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch

import pytest

from open_discourse.helper_functions.logging_config import setup_and_get_logger

# Definition Named Tuple for test cases, don't name it Testcase!!!
CaseDataforTest = namedtuple("CaseDataforTest", ["input", "expected", "exception"])


@pytest.fixture
def patch_log_path(tmp_path):
    """
    Patch LOG_DIR-path to tmp_path.

    Args:
        tmp_path (): pytest tmp_path

    Returns: patched LOG_DIR-path
    """

    # LOGS DIR
    mocked_LOGS_DIR = tmp_path / "logs"

    with patch("open_discourse.definitions.path_definitions.LOGS_DIR", mocked_LOGS_DIR):
        yield {"LOGS_DIR": mocked_LOGS_DIR}


# ========================================
# test cases for setup_and_get_logger
# ========================================
test_cases = []

# TC0: log line written
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": logging.INFO,
            "msg_level": logging.INFO,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.INFO, "This is a specific log text\n"),
        exception=None,
    )
)
# TC1: log line written into log-filename with dot
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_log.ging.whatever",
            "log_level": logging.WARNING,
            "msg_level": logging.ERROR,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.ERROR, "This is a specific log text\n"),
        exception=None,
    )
)
# TC2: log line NOT written due to lower msg_level
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": logging.INFO,
            "msg_level": logging.DEBUG,
            "msg_text": "This is a specific log text",
        },
        expected=(0, ""),
        exception=None,
    )
)
# TC3: bad log_level
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": 12,
            "msg_level": logging.DEBUG,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.DEBUG, "This is a specific log text\n"),
        exception=None,
    )
)
# TC3: bad log_level
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": "logging.WARNING",  # this i a string!
            "msg_level": logging.DEBUG,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.DEBUG, "This is a specific log text\n"),
        exception=None,
    )
)
# TC4: bad type msg_text
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "test_logging",
            "log_level": 12,
            "msg_level": logging.DEBUG,
            "msg_text": 153,
        },
        expected=(logging.DEBUG, "153\n"),
        exception=None,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_setup_and_get_logger(case: namedtuple, patch_log_path):
    log_filename = case.input["file_name"]
    log_file_path = Path(
        patch_log_path["LOGS_DIR"], str(Path(log_filename).stem + ".log")
    )

    # config logger with log_level from case.input
    logger = setup_and_get_logger(
        log_file=log_filename, log_level=case.input["log_level"]
    )

    # log file created?
    assert os.path.exists(log_file_path)

    log_config = {
        logging.DEBUG: ("DEBUG", logger.debug),
        logging.INFO: ("INFO", logger.info),
        logging.WARNING: ("WARNING", logger.warning),
        logging.ERROR: ("ERROR", logger.error),
        logging.CRITICAL: ("CRITICAL", logger.critical),
    }

    # write log line with msg_level and msg_text from case.input
    log_config[case.input["msg_level"]][1](case.input["msg_text"])

    # log line written as expected?
    with open(log_file_path, "r") as log_file:
        log_content = log_file.read()
        assert "ROOT" not in log_content
        if log_content:
            # check for correct log_level
            assert log_config[case.expected[0]][0] in log_content
            # assert case.expected[1] in log_content
            assert log_content.endswith(case.expected[1])
        else:
            assert case.expected[1] == log_content


test_cases = []
# TC0: wrong file_name type
test_cases.append(
    CaseDataforTest(
        {
            "file_name": logging,
            "log_level": logging.INFO,
            "msg_level": logging.INFO,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.INFO, "This is a specific log text"),
        exception=ValueError,
    )
)
# TC1: file_name too short
test_cases.append(
    CaseDataforTest(
        {
            "file_name": "lg",
            "log_level": logging.INFO,
            "msg_level": logging.INFO,
            "msg_text": "This is a specific log text",
        },
        expected=(logging.INFO, "This is a specific log text"),
        exception=ValueError,
    )
)


@pytest.mark.parametrize("case", test_cases)
def test_setup_and_get_logger_invalid_call(case: namedtuple, patch_log_path):
    # log_filename = case.input["file_name"]
    # log_file_path = Path(patch_log_path["LOGS_DIR"], log_filename)

    if case.exception:
        with pytest.raises(case.exception):
            logger = setup_and_get_logger(
                log_file=case.input["file_name"], log_level=case.input["log_level"]
            )
            logger.info("This is a specific invalid log text")
    else:
        assert False
