import asyncio
import os
import logging
from telethon import TelegramClient, events
from gcloud.aio.storage import Storage


TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL")
USERS_LIST = os.getenv("USERS_LIST")
GCS_FOLDER = os.getenv("GCS_FOLDER")
GCS_BUCKET = os.getenv("GCS_BUCKET")
GSA_CRED_PATH = os.getenv("GSA_CREDENTIAL_PATH")

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(module)s %(filename)s:%(lineno)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL))

bot = TelegramClient(session='bot', api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH, base_logger=logger)


async def get_bosses(users):
    Users = await bot.get_entity(users)
    users_ids = [i.id for i in Users]
    return users_ids


async def main():
    await bot.start(bot_token=TELEGRAM_TOKEN)

    users = USERS_LIST.split(",")
    bosses = await get_bosses(users)

    @bot.on(events.NewMessage(from_users=bosses, pattern="/upload (.*)", func=lambda e: e.media))
    async def uploadGCS(event):
        if event.photo:
            file = await event.download_media(file=bytes)
            fileName = event.pattern_match.group(1)
            async with Storage(service_file=GSA_CRED_PATH) as client:
                try:
                    status = await client.upload(GCS_BUCKET, f'{GCS_FOLDER}/{fileName}', file)
                    await event.reply(f"[Here is your URL]({status['mediaLink']})", parse_mode="markdown")
                except Exception as e:
                    logger.info(f"Failed to upload file with error: {e}", exc_info=True)
                    await event.reply("Failed to upload file. Please try again.")
        else:
            await event.reply("Please upload photo.")

    @bot.on(events.NewMessage(from_users=bosses, pattern="/del (.*)"))
    async def delFileGCS(event):
        async with Storage(service_file="/home/coder/tuanle-demo/gsa.json") as client:
            fileName = event.pattern_match.group(1)
            try:
                await client.delete(GCS_BUCKET, f'{GCS_FOLDER}/{fileName}')
                await event.reply(f"Successfully deleted file {fileName}")
            except Exception as e:
                logger.info("Got problem when deleting file on GCS: {e}", exc_info=True)
                await event.reply(f"Failed to delete file {fileName}. Please recheck the name of the file.")

    await bot.run_until_disconnected()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
