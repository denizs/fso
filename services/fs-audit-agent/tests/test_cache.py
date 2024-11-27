import os
from tempfile import NamedTemporaryFile

import pytest
from cache import FSOFileDiff


@pytest.fixture
def temp_file():
    """
    Creates a temporary file for testing and cleans up afterward.
    """
    with NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8") as tmp:
        tmp.write("Initial content\n")
        tmp_path = tmp.name
    yield tmp_path
    os.remove(tmp_path)


@pytest.fixture
def another_temp_file():
    """
    Creates another temporary file for testing and cleans up afterward.
    """
    with NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8") as tmp:
        tmp.write("Another file content\n")
        tmp_path = tmp.name
    yield tmp_path
    os.remove(tmp_path)


def test_add_file(temp_file):
    diff = FSOFileDiff()
    diff.add_file(temp_file)
    assert temp_file in diff.files
    assert diff.files[temp_file] == ["Initial content\n"]


def test_add_file_invalid_path():
    diff = FSOFileDiff()
    invalid_path = "/invalid/path/to/file.txt"
    diff.add_file(invalid_path)
    assert invalid_path not in diff.files


def test_add_file_duplicate(temp_file):
    diff = FSOFileDiff()
    diff.add_file(temp_file)
    # add the same file again
    diff.add_file(temp_file)
    # Ensure only one entry exists
    assert len(diff.files) == 1


def test_get_diff_no_change(temp_file):
    diff = FSOFileDiff()
    diff.add_file(temp_file)
    output = diff.get_diff(temp_file)
    assert len(list(output)) == 0  # No changes, so no diff output


def test_get_diff_with_change(temp_file):
    diff = FSOFileDiff()
    diff.add_file(temp_file)

    # Modify the file content
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write("Modified content\n")

    diff_output = list(diff.get_diff(temp_file))
    # now we want to check if the diff is correct...
    assert "--- previous_version" in diff_output
    assert "+++ current_version" in diff_output
    assert "-Initial content\n" in diff_output
    assert "+Modified content\n" in diff_output


def test_get_diff_file_not_monitored(another_temp_file):
    diff = FSOFileDiff()
    output = diff.get_diff(another_temp_file)
    assert output is None  # File not monitored, so no diff


def test_state_update_after_update(temp_file):
    diff = FSOFileDiff()
    diff.add_file(temp_file)

    # Modify the file content
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write("Modified content\n")

    # we expect the updated content after update was called.
    diff.update_cache(temp_file)
    assert diff.files[temp_file] == ["Modified content\n"]  # Verify state is updated


def test_rekey_ok(temp_file, another_temp_file):
    diff = FSOFileDiff()
    diff.add_file(temp_file)

    # let's rekey - like after moving a to b
    diff.rekey(temp_file, another_temp_file)

    # assert new file location is old file content. move worked.
    assert diff.files[another_temp_file] == ["Initial content\n"]
