import base64
import socket
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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

    class Config:
        schema_extra = {
            "example": {
                "emitter": "my-hostname",
                "event_type": "moved",
                "timestamp": "2024-11-24T10:15:30.456Z",
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
