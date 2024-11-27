"""Cache important files and allow comparison"""

import difflib
import os


class FSOFileDiff:
    def __init__(self):
        self.files = {}

    def _read_file(self, file_path: str) -> list[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.readlines()
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return []

    def add_file(self, file_path: str) -> None:
        """
        Adds a file to be monitored for diffs. This should be done
        once to populate the cache.
        Validates that the path is a file.
        :param file_path: Path to the file to monitor.
        """
        if not os.path.isfile(file_path):
            print(f"Error: '{file_path}' is not a valid file.")
            return

        if file_path in self.files:
            print(f"File '{file_path}' is already being monitored.")
            return

        self.update_cache(file_path)
        print(f"File '{file_path}' added for monitoring.")

    def rekey(self, old_path: str, new_path: str) -> None:
        """keys can change when a file is moved. Tell the cache to track with new key"""
        try:
            self.files.update({new_path: self.files.pop(old_path)})
        except KeyError as e:
            print(f"Cache Re-Keying failed for {old_path}")
            self.add_file(new_path)

    def update_cache(self, file_path: str) -> None:
        """
        Update the file cache. This potentially overrides existing
        cache content.
        """
        self.files[file_path] = self._read_file(file_path)

    def get_diff(self, file_path: str):
        """
        Creates a diff for the specified file and prints it to stdout.
        Side effect: if the file wasn't cached before, add it to the cache...
        :param file_path: Path to the file to generate the diff for.
        """
        if file_path not in self.files:
            print(f"File '{file_path}' is not being monitored.")
            return

        current_content = self._read_file(file_path)
        previous_content = self.files[file_path]

        if not previous_content:
            print(f"No previous content to compare for file '{file_path}'.")
            # add it to the diff just in case...
            self.add_file(file_path)

        # create a diff using difflib...
        diff = difflib.unified_diff(
            previous_content,
            current_content,
            fromfile="previous_version",
            tofile="current_version",
            lineterm="",
        )
        # print("\n".join(diff))
        return diff
