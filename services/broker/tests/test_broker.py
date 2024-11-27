from unittest.mock import AsyncMock, MagicMock

import pytest

from broker import FSOBroker


@pytest.fixture
def broker():
    """Fixture to provide an instance of FSOBroker."""
    return FSOBroker()


@pytest.fixture
def mock_writer():
    """Fixture to create a mock writer."""
    writer = MagicMock()
    writer.drain = AsyncMock()  # Mock the drain method
    return writer


@pytest.mark.asyncio
async def test_subscribe(broker, mock_writer):
    """Test subscribing a client to a topic."""
    topic = "test/topic"
    broker.subscribe(mock_writer, topic)

    # Verify the writer is in the subscriptions for the topic
    assert topic in broker.subscriptions
    assert mock_writer in broker.subscriptions[topic]


@pytest.mark.asyncio
async def test_publish_to_subscribed_client(broker, mock_writer):
    """Test publishing a message to a subscribed client."""
    topic = "test/topic"
    payload = "Hello, Subscriber!"

    broker.subscribe(mock_writer, topic)
    await broker.publish(topic, payload)

    # Verify the writer received the message
    mock_writer.write.assert_called_once_with(f"{topic} {payload}\n".encode("utf-8"))
    mock_writer.drain.assert_awaited_once()


@pytest.mark.asyncio
async def test_publish_with_no_subscribers(broker):
    """Test publishing a message to a topic with no subscribers."""
    topic = "test/topic"
    payload = "Hello, no one!"

    # Attempt to publish without any subscribers
    await broker.publish(topic, payload)

    # Verify no exceptions and no messages sent
    assert len(broker.subscriptions) == 0


@pytest.mark.asyncio
async def test_disconnect(broker, mock_writer):
    """Test disconnecting a client."""
    topic = "test/topic"
    broker.subscribe(mock_writer, topic)

    # Disconnect the mock_writer
    broker.disconnect(mock_writer)

    # Verify the writer is no longer subscribed
    assert mock_writer not in broker.subscriptions[topic]


@pytest.mark.asyncio
async def test_topic_matches_exact(broker):
    """Test topic matching for an exact match."""
    topic = "test/topic"
    assert broker.topic_matches(topic, topic) is True


@pytest.mark.asyncio
async def test_topic_matches_wildcard(broker):
    """Test topic matching with a wildcard."""
    subscription = "test/~"
    topic = "test/topic"

    assert broker.topic_matches(subscription, topic) is True


@pytest.mark.asyncio
async def test_handle_client_subscribe_and_publish(broker):
    """Test handling client subscription and publishing."""

    # let's create a fake connection again...
    reader = MagicMock()
    writer = AsyncMock()
    writer.get_extra_info.return_value = ("127.0.0.1", 12345)

    # Simulate client actions
    reader.read = AsyncMock(
        side_effect=[
            b"SUBSCRIBE test/topic\n",
            b"PUBLISH test/topic Hello!\n",
        ],
    )

    await broker.handle_client(reader, writer)

    # Verify subscription exists...
    assert "test/topic" in broker.subscriptions

    # Verify message sent back to the writer
    writer.write.assert_any_call(b"test/topic Hello!\n")
    writer.close.assert_called_once()
