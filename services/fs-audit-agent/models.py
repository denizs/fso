import base64
import re
import socket
from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class FileObserverEvent(BaseModel):
    """
    Model representing a file system event message.
    """

    emitter: str = Field(
        default_factory=socket.gethostname,
        description="Client ID, typically the hostname.",
    )
    event_type: Literal["created", "modified", "deleted", "moved"] = Field(
        ...,
        description="Type of the file system event.",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of the event.",
    )
    file_path: str = Field(..., description="Path of the file affected by the event.")
    destination_path: str | None = Field(
        None,
        description="Destination path if the event is a move operation.",
    )
    diff: List[str] | None = Field(
        None,
        description="A list of file diff lines",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "emitter": "my-hostname",
                "event_type": "moved",
                "timestamp": "2024-11-24T09:30:30.456Z",
                "file_path": "/path/to/source/file.txt",
                "destination_path": "/path/to/destination/file.txt",
            },
        }

    def to_base64(self) -> str:
        """
        Serialize the event to a Base64-encoded string.
        """
        json_str = self.json()
        base64_bytes = base64.b64encode(json_str.encode("utf-8"))
        return base64_bytes.decode("utf-8")

    @classmethod
    def from_base64(cls, base64_str: str) -> "FileObserverEvent":
        """
        Deserialize a Base64-encoded string back into a FileObserverEvent.
        """
        json_str = base64.b64decode(base64_str).decode("utf-8")
        return cls.model_validate_json(json_str)


class FileObserverRule(BaseModel):
    """
    Model representing file observer rules.
    """

    exclude_patterns: List[str] = Field(
        ...,
        description="A list of regular expressions to exclude files or directories from observation.",
    )
    important_pattern: List[str] = Field(
        ...,
        description="A list of regular expression to match files or directories marked as important.",
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of when the rule was last updated.",
    )

    @field_validator("exclude_patterns", "important_pattern")
    def validate_regex(cls, pattern: list[str]) -> str:
        """
        Validate that each pattern is a valid regular expression.
        """
        try:
            p_comp = [re.compile(p) for p in pattern]
        except re.error as e:
            raise ValueError(f"Invalid pattern: {pattern}. Error: {e}")
        return p_comp

    class Config:
        json_schema_extra = {
            "example": {
                "exclude_patterns": [
                    r"^.*\.tmp$",  # Exclude temporary files
                    r"^.*__pycache__$",  # Exclude __pycache__ directories
                    r"^.*\.log$"  # Exclude log files
                    r"^.*/joe/.*$",  # ignore joes private files
                ],
                "important_pattern": [
                    r"^.*\.conf$",  # Match configuration files as important
                    r"^.*/important_stuff/.*$",
                ],
                "last_updated": "2024-11-24T11:15:30.456Z",
            },
        }
