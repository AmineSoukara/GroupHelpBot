import asyncio
import io
import os
from datetime import datetime

import requests
from telethon import events
from telethon import types
from telethon.tl import functions

from auditor import LOGGER
from auditor import REM_BG_API_KEY
from auditor import client
from auditor import TEMP_DOWNLOAD_DIRECTORY
from auditor.events import register


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (await
             client(functions.channels.GetParticipantRequest(chat,
                                                           user))).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await client.get_peer_id(user)
        ps = (await client(functions.messages.GetFullChatRequest(chat.chat_id)
                         )).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    else:
        return None


@register(pattern="^/removebg")
async def _(event):
    HELP_STR = "use `/rmbg` as reply to a media"
    if event.fwd_from:
        return
    if event.is_group:
        if not (await is_register_admin(event.input_chat,
                                        event.message.sender_id)):
            return
    if REM_BG_API_KEY is None:
        await event.reply(
            "You need API token from remove.bg to use this plugin.")
        return False
    start = datetime.now()
    message_id = event.message.id
    if event.reply_to_msg_id:
        message_id = event.reply_to_msg_id
        reply_message = await event.get_reply_message()
        # check if media message
        await event.reply("Processing...")
        try:
            downloaded_file_name = await event.client.download_media(
                reply_message, TEMP_DOWNLOAD_DIRECTORY)
        except Exception as e:
            await event.reply(str(e))
            return
        else:
            output_file_name = ReTrieveFile(downloaded_file_name)
            os.remove(downloaded_file_name)
    else:
        await event.reply(HELP_STR)
        return
    contentType = output_file_name.headers.get("content-type")
    if "image" in contentType:
        with io.BytesIO(output_file_name.content) as remove_bg_image:
            remove_bg_image.name = "ebruiser.png"
            await event.client.send_file(
                event.chat_id,
                remove_bg_image,
                force_document=True,
                supports_streaming=False,
                allow_cache=False,
                reply_to=message_id,
            )
        end = datetime.now()
        ms = (end - start).seconds
        await event.reply("Ebruiser-Space Successfully Removed Background in {} seconds".format(ms))
    else:
        await event.reply(
            "Check if it is really an image ?...Still not solved Report to @EBRUISER \n`{}"
            .format(output_file_name.content.decode("UTF-8")))


# this method will call the API, and return in the appropriate format
# with the name provided.
def ReTrieveFile(input_file_name):
    headers = {
        "X-API-Key": REM_BG_API_KEY,
    }
    files = {
        "image_file": (input_file_name, open(input_file_name, "rb")),
    }
    r = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers=headers,
        files=files,
        allow_redirects=True,
        stream=True,
    )
    return r
