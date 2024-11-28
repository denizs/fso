# Audit Agent README

## Overview

The **FSO Audit Agent** is a client for subscribing to a message broker and recording received messages in the **JSON Line Protocol** format. It connects to the broker, subscribes to topics, processes incoming messages, decodes their payloads, and writes the messages to a specified log file for auditing purposes.

## Features

- Connects to a message broker via TCP.
- Subscribes to topics.
- Receives messages, decodes Base64-encoded payloads.
- Logs messages to a file in **JSON Line Protocol** format to a predefined location.

## JSON Line Format

Each line in the log file represents a single message and is written in **JSON Line Protocol** (JSONL). The format of each line is:

```json
{
  "topic": "/path/of/modified/file.txt,
  "payload": <payload>
}
```

Where:

- topic: The topic under which the message was published. This is a string.
- payload: The decoded and parsed JSON payload sent with the message. This is a JSON object.

**Example** of one record in the audit.jsonl:

```json
{"topic": "/tmp/enlyze/important_stuff/foo.txt", "payload": {"emitter": "carbon", "event_type": "modified", "timestamp": "2024-11-26T18:15:52.323819", "file_path": "/tmp/enlyze/important_stuff/foo.txt", "destination_path": null, "diff": ["-- previous_version", "++ current_version", "1c2d3e"]}}

```
