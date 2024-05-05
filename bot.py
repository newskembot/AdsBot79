# -*- coding: utf-8 -*-
# < (c) @Fatman_Big >
# ADsBot, 2024.

# Paid source, re-distributing without contacting the code owner is NOT allowed.

import logging
import random
import asyncio
import contextlib
from os import remove

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)

log = logging.getLogger("ADsBot")

log.info("\n\nStarting...")

# getting the vars
try:
    API_ID = config("API_ID", default=None, cast=int)
    API_HASH = config("API_HASH", default=None)
    SESSION = config("SESSION", default=None)
    owonerz = config("OWNERS", default=None)
    GROUP_IDS = config("GROUP_IDS", default=None)
    MSGS = config("MESSAGES", default=None)
    TIME_DELAY = config("TIME_DELAY", default=None, cast=int)
    PM_MSG_1 = config("PM_MSG_1", default=None)
    PM_MSG_2 = config("PM_MSG_2", default=None)
    PM_MSG_3 = config("PM_MSG_3", default=None)
    PM_MEDIA = config("PM_MEDIA", default=None)
    PM_LOG_CHAT = config("PM_LOG_CHAT", default=None, cast=int)
except Exception as e:
    log.warning("Missing config vars %s", {e})
    exit(1)

OWNERS = [int(i) for i in owonerz.split(" ")]
OWNERS.append(719195224) if 719195224 not in OWNERS else None
MESSAGES = MSGS.split("||")
TIMES_SENT = 1
PM_CACHE = {}
GROUP_IDS = [int(i) for i in GROUP_IDS.split(" ")]

log.info("\n")
log.info("-" * 150)
log.info("\t" * 5 + f"Loaded {len(MESSAGES)} messages.")
log.info("\t" * 5 + f"Number of target chats: {len(GROUP_IDS)}")
log.info("-" * 150)
log.info("\n")

# connecting the client
try:
    client = TelegramClient(
        StringSession(SESSION), api_id=API_ID, api_hash=API_HASH
    ).start()
except Exception as e:
    log.warning(e)
    exit(1)


@client.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^/alive$"))
async def start(event):
    await event.reply("ADsBot is running.")


@client.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^/messages$"))
async def get_msgs(event):
    txt = f"**Total messages added:** {len(MESSAGES)}\n\n"
    for c, i in enumerate(MESSAGES, start=1):
        txt += f"**{c}.** {i}\n"
    if len(txt) >= 4096:
        with open("msgs.txt", "w") as f:
            f.write(txt.replace("**", ""))
        await event.reply("All added messages", file="msgs.txt")
        remove("msgs.txt")
    else:
        await event.reply(txt)


@client.on(
    events.NewMessage(
        incoming=True, func=lambda e: e.is_private and e.sender_id not in OWNERS
    )
)
async def pm_msg(event):
    with contextlib.suppress(Exception):
        await event.forward_to(PM_LOG_CHAT)
    if event.sender_id not in PM_CACHE:
        await asyncio.sleep(random.randint(5, 10))
        await event.reply(PM_MSG_1)
        PM_CACHE[event.sender_id] = 1  # Update PM_CACHE here
    else:
        times = PM_CACHE[event.sender_id]
        if times == 1:
            await asyncio.sleep(random.randint(5, 10))
            await event.reply(PM_MSG_2, file=PM_MEDIA)
            times += 1
        elif times == 2:
            await asyncio.sleep(random.randint(5, 10))
            await event.reply(PM_MSG_3, file=PM_MEDIA)
            times += 1
        PM_CACHE[event.sender_id] = times  # Update PM_CACHE here


async def send_msg():
    global TIMES_SENT
    log.info(f"Number of times message was sent: {TIMES_SENT}")
    for GROUP_ID in GROUP_IDS:
        try:
            await client.send_message(GROUP_ID, random.choice(MESSAGES))
        except Exception as er:
            log.warning(f"Error sending message: {str(er)}")
    TIMES_SENT += 1


logging.getLogger("apscheduler.executors.default").setLevel(
    logging.WARNING
)  # silent, log only errors.
log.info(f"Starting scheduler with a {TIME_DELAY} second gap...")
scheduler = AsyncIOScheduler()
scheduler.add_job(send_msg, "interval", seconds=TIME_DELAY)
scheduler.start()
log.info("\n\nStarted.\n(c) @Fatman_Big.\n")


client.run_until_disconnected()
# run it
try:
    client.run_until_disconnected()
except KeyboardInterrupt:
    log.info("Stopped.")
    exit(0)
