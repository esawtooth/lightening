import json
import logging
import os
from datetime import datetime

import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import openai

from events import Event, LLMChatEvent

SERVICEBUS_CONN = os.environ.get("SERVICEBUS_CONNECTION")
SERVICEBUS_QUEUE = os.environ.get("SERVICEBUS_QUEUE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

missing = []
if not SERVICEBUS_CONN:
    missing.append("SERVICEBUS_CONNECTION")
if not SERVICEBUS_QUEUE:
    missing.append("SERVICEBUS_QUEUE")
if not OPENAI_API_KEY:
    missing.append("OPENAI_API_KEY")
if missing:
    logging.error("Missing required environment variable(s): %s", ", ".join(missing))
    raise RuntimeError("Azure Function misconfigured")

client = ServiceBusClient.from_connection_string(SERVICEBUS_CONN)


def main(msg: func.ServiceBusMessage) -> None:
    body = msg.get_body().decode("utf-8")
    try:
        data = json.loads(body)
        event = LLMChatEvent.from_dict(data)
    except Exception as e:
        logging.error("Invalid event: %s", e)
        return

    try:
        response = openai.ChatCompletion.create(
            messages=event.messages,
            model=OPENAI_MODEL,
        )
        reply = response["choices"][0]["message"]["content"]
        usage = response.get("usage")
        logging.info("Assistant reply: %s", reply)
    except Exception as e:
        logging.error("ChatCompletion failed: %s", e)
        return

    out_event = Event(
        timestamp=datetime.utcnow(),
        source="ChatResponder",
        type="llm.chat.response",
        user_id=event.user_id,
        metadata={"reply": reply, "usage": usage},
        history=event.history + [event.to_dict()],
    )

    message = ServiceBusMessage(json.dumps(out_event.to_dict()))
    message.application_properties = {"topic": out_event.type}

    try:
        with client:
            sender = client.get_queue_sender(queue_name=SERVICEBUS_QUEUE)
            with sender:
                sender.send_messages(message)
    except Exception as e:
        logging.error("Failed to publish response: %s", e)
