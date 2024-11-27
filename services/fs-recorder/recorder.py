import asyncio
import base64
import json


class AsyncMQTTClient:
    def __init__(self, host: str, port: int, topic: str):
        self.host = host
        self.port = port
        self.topic = topic
        self.reader = None
        self.writer = None

    async def connect(self):
        """Connects to the broker."""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        print(f"Connected to {self.host}:{self.port}")
        # Send the SUBSCRIBE command
        await self.subscribe()

    async def subscribe(self):
        """Sends a subscription request to the broker."""
        command = f"SUBSCRIBE {self.topic}\n"
        self.writer.write(command.encode("utf-8"))
        await self.writer.drain()
        print(f"Subscribed to topic: {self.topic}")

    async def process_messages(self):
        """Processes messages from the broker."""
        try:
            while True:
                # Read a line from the broker
                line = await self.reader.readline()
                if not line:
                    print("Connection closed by broker.")
                    break

                # Decode the line and process
                message = line.decode("utf-8").strip()
                await self.handle_message(message)
        except asyncio.CancelledError:
            print("Message processing task was cancelled.")
        finally:
            self.disconnect()

    async def handle_message(self, message: str):
        """Handles an incoming message."""
        try:
            # Split the message into topic and payload
            topic, payload = message.split(" ")[-2:]
            print(f"Topic: {topic}")

            # Decode the payload from Base64
            decoded_payload = base64.b64decode(payload).decode("utf-8")
            # Parse JSON and pretty-print it
            parsed_payload = json.loads(decoded_payload)
            print(json.dumps(parsed_payload, indent=4))
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Failed to process message: {message}\nError: {e}")

    def disconnect(self):
        """Closes the connection to the broker."""
        if self.writer:
            self.writer.close()
            print("Disconnected from broker.")


# Async main function
async def main():
    host = "127.0.0.1"  # Broker host
    port = 1883  # Broker port
    topic = "/tmp/enlyze~"  # Topic to subscribe to

    client = AsyncMQTTClient(host, port, topic)
    await client.connect()

    # Start processing messages
    await client.process_messages()


# Run the async client
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Client stopped.")
