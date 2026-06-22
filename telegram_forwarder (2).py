from telethon import TelegramClient
from telethon.tl.functions.messages import ForwardMessagesRequest
import asyncio
import logging
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

API_ID = 31620520
API_HASH = "PASTE_YOUR_NEW_API_HASH_HERE"
SESSION_NAME = "forwarder_session"

SOURCE_CHANNEL = "synogu"
MESSAGE_ID_TO_FORWARD = 15
INTERVAL_HOURS = 1  # change to 2, 3 etc. to send less often

TARGET_CHANNELS = [
    {"channel": "flips"},
    {"channel": "marketunlimited", "topic_id": 74145, "no_preview": True},
    {"channel": "rarehandle", "topic_id": 85, "no_preview": True},
    {"channel": "mqrkt", "no_preview": True},
    {"channel": "TradeMarketHub"},
]

FORWARD_DELAY = 2.0

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def forward_message(message):
    success, failed = 0, 0
    for entry in TARGET_CHANNELS:
        channel = entry["channel"]
        topic_id = entry.get("topic_id")
        no_preview = entry.get("no_preview", False)
        try:
            if topic_id and no_preview:
                entity = await client.get_entity(channel)
                text = message.text or message.caption or ""
                await client.send_message(entity, text, reply_to=topic_id, link_preview=False)
                logger.info(f"Sent to {channel} topic {topic_id} (no preview)")
            elif topic_id:
                entity = await client.get_entity(channel)
                await client(ForwardMessagesRequest(
                    from_peer=message.peer_id,
                    id=[message.id],
                    to_peer=entity,
                    top_msg_id=topic_id,
                    random_id=[random.randint(0, 2**31)],
                ))
                logger.info(f"Forwarded to {channel} (topic {topic_id})")
            elif no_preview:
                text = message.text or message.caption or ""
                await client.send_message(channel, text, link_preview=False)
                logger.info(f"Sent to {channel} (no preview)")
            else:
                await client.forward_messages(channel, message)
                logger.info(f"Forwarded to {channel}")
            success += 1
        except Exception as e:
            logger.error(f"Failed to forward to {channel}: {e}")
            failed += 1
        await asyncio.sleep(FORWARD_DELAY)
    logger.info(f"Done - {success} succeeded, {failed} failed.")


async def main():
    await client.start()
    logger.info("Client started and authenticated.")
    while True:
        message = await client.get_messages(SOURCE_CHANNEL, ids=MESSAGE_ID_TO_FORWARD)
        if not message:
            logger.error(f"Message ID {MESSAGE_ID_TO_FORWARD} not found in {SOURCE_CHANNEL}.")
        else:
            logger.info(f"Forwarding message {MESSAGE_ID_TO_FORWARD} from {SOURCE_CHANNEL}...")
            await forward_message(message)
        logger.info(f"Sleeping for {INTERVAL_HOURS} hour(s)...")
        await asyncio.sleep(INTERVAL_HOURS * 3600)


if __name__ == "__main__":
    asyncio.run(main())
