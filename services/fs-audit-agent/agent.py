import asyncio

from models import FileObserverEvent
from watchdog.events import (
    DirCreatedEvent,
    DirDeletedEvent,
    DirModifiedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer


class FSOMessageClient:
    def __init__(self, host="127.0.0.1", port=1883):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        """Connect to the broker."""
        # TODO: add retry logic
        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port,
        )
        print(f"Connected to FOSBroker at {self.host}:{self.port}")

    async def disconnect(self) -> None:
        """Disconnect from the broker."""
        if self.writer:
            self.writer.write("DISCONNECT\n".encode("utf-8"))
            await self.writer.drain()
            self.writer.close()
            await self.writer.wait_closed()
            print("Disconnected from FOSBroker")

    async def subscribe(self, topic: str) -> None:
        """Subscribe to a topic."""
        if self.writer:
            command = f"SUBSCRIBE {topic}\n"
            self.writer.write(command.encode("utf-8"))
            await self.writer.drain()
            print(f"Subscribed to topic: {topic}")

    async def publish(self, topic: str, message: str) -> None:
        """Publish a message to a topic."""
        if self.writer:
            command = f"PUBLISH {topic} {message}\n"
            self.writer.write(command.encode("utf-8"))
            await self.writer.drain()
            print(f"Published to {topic}: {message}")

    async def listen(self) -> None:
        """Listen for incoming messages from the broker."""
        if self.reader:
            while True:
                data = await self.reader.readline()
                if not data:
                    break
                print(f"Received: {data.decode('utf-8').strip()}")
                # TODO: Handle filter rule updates....


class FileHandler(FileSystemEventHandler):

    def __init__(self, client: FSOMessageClient, config: dict) -> None:
        super().__init__()
        self.client = client
        self.__loop = asyncio.get_event_loop()

    def __emit(self, topic: str, msg: FileObserverEvent) -> None:
        pub_co = self.client.publish(topic, msg.to_base64())
        self.__loop.create_task(pub_co)

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent) -> None:
        print(f"File {event.src_path} has been modified")
        msg = FileObserverEvent(
            event_type="modified",
            file_path=event.src_path,
        )
        self.__emit(event.src_path, msg)

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent) -> None:
        print(f"File {event.src_path} has been created")
        msg = FileObserverEvent(
            event_type="created",
            file_path=event.src_path,
        )
        self.__emit(event.src_path, msg)

    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        print(f"File {event.src_path} has been moved to {event.dest_path}")
        msg = FileObserverEvent(
            event_type="moved",
            file_path=event.src_path,
            destination_path=event.dest_path,
        )
        self.__emit(event.src_path, msg)

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent) -> None:
        print(f"File {event.src_path} has been deleted")
        msg = FileObserverEvent(
            event_type="deleted",
            file_path=event.src_path,
            destination_path=event.dest_path,
        )
        self.__emit(event.src_path, msg)


class FSOFileObserver:
    """
    Observes a given path for file changes.
    """

    def __init__(self, path_to_watch: str, file_handler: FileHandler):
        self.path_to_watch = path_to_watch
        self.event_handler = file_handler
        self.observer = Observer()

    def start(self):
        """
        Start observing the path for changes.
        """
        self.observer.schedule(self.event_handler, self.path_to_watch, recursive=True)
        self.observer.start()
        print(f"Started monitoring {self.path_to_watch}.")

    def stop(self):
        """
        Stop observing the path.
        """
        self.observer.stop()
        self.observer.join()
        print(f"Stopped monitoring {self.path_to_watch}.")


async def run_agent():
    # TODO: make this configurable
    path = "/tmp/enlyze"

    client = FSOMessageClient()
    handler = FileHandler(client, config={})
    file_observer = FSOFileObserver(
        path_to_watch=path,
        file_handler=handler,
    )

    await client.connect()
    file_observer.start()
    while True:
        await asyncio.sleep(1)  # Keep the script running


if __name__ == "__main__":
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("FSO-Agent stopping...")
