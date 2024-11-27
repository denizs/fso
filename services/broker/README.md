# FSO-Broker

**FSO-Broker** is a lightweight, no-dependency, asynchronous Python-based message broker designed for simple topic-based communication between clients. It supports subscribing to topics, publishing messages, and basic wildcard topic matching.
It does not support wildcard topics, any kind of authentication or fail-safety.

## Features
- **Topic-based Messaging:** Clients can subscribe to specific topics and receive messages published to those topics.
- **Wildcard Support:** Allows partial topic matching using the `~` wildcard for flexible subscriptions.
- **Asynchronous Operation:** Built using `asyncio` for handling multiple clients concurrently.

---

## Commands
Clients interact with FSOBroker using simple text-based commands:

### 1. **SUBSCRIBE**
   - **Purpose:** Subscribe to a topic to receive messages.
   - **Format:** `SUBSCRIBE <topic>`
   - **Example:**
     ```text
     SUBSCRIBE /home/enlyze/~
     ```

### 2. **PUBLISH**
   - **Purpose:** Publish a message to a topic.
   - **Format:** `PUBLISH <topic> <message>`
   - **Example:**
     ```text
     PUBLISH /enlyze/sys/class/thermal/thermal_zone0/temp 4900
     ```

### 3. **DISCONNECT**
   - **Purpose:** Disconnect the client from the broker.
   - **Format:** `DISCONNECT`

---

## Wildcard Matching
Topics can include a `~` wildcard to subscribe to groups of topics:
- **Example Subscription:** `SUBSCRIBE sensor/~`
  - Matches any topic starting with `sensor/`, such as `sensor/temperature` or `sensor/humidity`.

---

## Configuration

### Default Configuration:
- **Host:** `127.0.0.1`
- **Port:** `1883`

### How to Start the Broker
1. Clone or download the repository containing FSOBroker.
2. Run the broker script:
   ```bash
   python fso_broker.py
   ```
3. success...


you can test the broker using telnet

```bash
telnet 127.0.0.1 1883
SUBSCRIBE test/topic
PUBLISH test/topic Hello, FSOBroker!
```
