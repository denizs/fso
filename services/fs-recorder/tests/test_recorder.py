from unittest.mock import AsyncMock, patch

import pytest

from recorder import FSORecorderClient


@pytest.fixture
def client():
    return FSORecorderClient(
        host="127.0.0.1",
        port=1883,
        topic="/tmp/enlyze~",
        logfile="./test_audit.jsonl",
    )


@pytest.mark.asyncio
async def test_connect(client):
    """Test that the client connects to the broker and subsriber."""
    with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_connection:
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        # pretend we have a connection...
        mock_connection.return_value = (mock_reader, mock_writer)

        await client.connect()

        assert client.reader == mock_reader
        assert client.writer == mock_writer
        # we want to make sure we called subscribe only once.
        client.writer.write.assert_called_once_with(
            b"SUBSCRIBE /tmp/enlyze~\n",
        )


@pytest.mark.asyncio
async def test_process_messages(client):
    """Test that the client processes messages correctly."""
    with patch.object(
        client,
        "handle_message",
        new_callable=AsyncMock,
    ) as mock_handle_message:
        mock_reader = AsyncMock()
        client.reader = mock_reader
        mock_reader.readline.side_effect = [
            b"/tmp/enlyze/test_topic eyJrZXkiOiAiVmFsdWUifQ==\n",
            b"",
        ]
        mock_writer = AsyncMock()
        client.writer = mock_writer

        await client.process_messages()
        mock_handle_message.assert_called_once_with(
            "/tmp/enlyze/test_topic eyJrZXkiOiAiVmFsdWUifQ==",
        )
        assert mock_writer.close.called


@pytest.mark.asyncio
async def test_handle_message_invalid_message(client):
    """Test that handle_message handles invalid messages gracefully."""
    invalid_message = "invalid_message_without_topic_and_payload"

    with patch("builtins.print") as mock_print:
        await client.handle_message(invalid_message)

        # Verify the error message was printed
        assert "Failed to process message" in mock_print.call_args[0][0]


@pytest.mark.asyncio
async def test_disconnect(client):
    """Test that the client disconnects properly."""
    mock_writer = AsyncMock()
    client.writer = mock_writer

    client.disconnect()

    mock_writer.close.assert_called_once()
