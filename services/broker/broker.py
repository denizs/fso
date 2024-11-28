import asyncio
from collections import defaultdict


class FSOBroker:
    def __init__(self):
        # topic -> list of (writer, wildcard)
        self.subscriptions = defaultdict(list)
        self.clients = []

    async def handle_client(self, reader, writer):
        """Handle an individual client connection."""
        self.clients.append(writer)
        addr = writer.get_extra_info("peername")
        print(f"Client connected: {addr}")

        try:
            while data := await reader.read(1024):
                message = data.decode("utf-8").strip()
                if message.startswith("SUBSCRIBE"):
                    # handle subsribe actions
                    topic = message.split(" ", 1)[1]
                    self.subscribe(writer, topic)
                elif message.startswith("PUBLISH"):
                    # handle publish action
                    _, topic, payload = message.split(" ", 2)
                    await self.publish(topic, payload)
                elif message == "DISCONNECT":
                    break
        except Exception as e:
            print(f"Error with client {addr}: {e}")
        finally:
            self.disconnect(writer)
            # close the remote connection
            print(f"Client disconnected: {addr}")

    def subscribe(self, writer, topic):
        """
        Subscribe a client to a topic.
        We need to map topics to subsribed clients
        """
        print(f"Subscribing client to topic: {topic}")
        self.subscriptions[topic].append(writer)

    async def publish(self, topic, payload):
        """Publish a message to a topic."""
        print(f"Publishing to {topic}: {payload}")
        for sub_topic, writers in self.subscriptions.items():
            if self.topic_matches(sub_topic, topic):
                for writer in writers:
                    try:
                        writer.write(f"{topic} {payload}\n".encode("utf-8"))
                        await writer.drain()
                    except Exception as e:
                        print(f"Error sending to client: {e}")

    def topic_matches(self, sub_topic, topic):
        """
        Logic to decide if a subscription matches the topic.
        The can handle tilde ('~') symbols as wildcard. Everything
        after the tilde matches the remaining topic. Otherwise, we
        expect an exact match.
        """
        # tilde match logic
        if "~" in sub_topic:
            before_match = sub_topic.split("~")[0]
            if topic.startswith(before_match):
                # partial match
                return True
        if topic == sub_topic:
            # exact match
            return True
        return False

    def disconnect(self, writer):
        """Disconnect a client and clean up subscriptions."""
        for topic in self.subscriptions.keys():
            self.subscriptions[topic] = [
                w for w in self.subscriptions[topic] if w != writer
            ]
        if writer in self.clients:
            self.clients.remove(writer)
        writer.close()


async def main():
    broker = FSOBroker()
    server = await asyncio.start_server(
        # For demonstration, we run the server on localhost
        broker.handle_client,
        "0.0.0.0",
        1883,
    )
    addr = server.sockets[0].getsockname()
    print(f"Serving FSOBroker on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
