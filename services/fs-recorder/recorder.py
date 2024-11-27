import asyncio
import base64
import json
import os

import aiofiles


class FSORecorderClient:
    def __init__(self, host: str, port: int, topic: str, logfile: str):
        self.host = host
        self.port = port
        self.topic = topic
        self.file_path = logfile
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

    async def __log_line(self, topic: str, payload: dict):
        """
        Asynchronously writes a message with topic and payload
        in JSON Line Protocol format to the specified file.
        """
        # Ensure the directory for the file exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        json_line = {
            "topic": topic,
            "payload": payload,
        }

        # open file append mode...
        async with aiofiles.open(self.file_path, "a", encoding="utf-8") as f:
            await f.write(json.dumps(json_line) + "\n")

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

            # Log it to a file
            await self.__log_line(topic, parsed_payload)

        except (ValueError, json.JSONDecodeError) as e:
            print(f"Failed to process message: {message}\nError: {e}")

    def disconnect(self):
        """Closes the connection to the broker."""
        if self.writer:
            self.writer.close()
            print("Disconnected from broker.")


async def main(host, port, topic, logfile):
    logfile = os.path.abspath(logfile)

    client = FSORecorderClient(host, port, topic, logfile)
    await client.connect()

    # Start processing messages
    await client.process_messages()


# Run the async client
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=str, help="broker address", default="127.0.0.1")
    parser.add_argument("-p", type=int, help="broker port", default=1883)
    parser.add_argument("-t", type=str, help="topic string", default="/tmp/enlyze~")
    parser.add_argument("-l", type=str, help="log file path", default="./audit.log")

    args = parser.parse_args()
    try:
        asyncio.run(main(args.c, args.p, args.t, args.l))
    except KeyboardInterrupt:
        print("FSO Recorder stopped.")
