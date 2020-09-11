from telethon import events
from random import randrange
from telegram.ext.dispatcher import run_async
from auditor.modules.helper_funcs.alternate import send_message, typing_action
import io
import asyncio
import time
import glob
import os
from auditor import LOGGER, client
from telethon import types
from telethon.tl import functions
from auditor import client
from telethon import events
import os
import requests
import json
import bs4
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from coffeehouse.lydia import LydiaAI
from coffeehouse.api import API
import asyncio
from telethon import events
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

import coffeehouse as cf

from auditor.events import register

import asyncio
import io
import coffeehouse
from auditor import LYDIA_API_KEY
from telethon import events
from coffeehouse.lydia import LydiaAI
from coffeehouse.api import API

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (await client(functions.channels.GetParticipantRequest(chat, user))).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator)
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await client.get_peer_id(user)
        ps = (await client(functions.messages.GetFullChatRequest(chat.chat_id))) \
            .full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator)
        )
    else:
        return None


# Non-SQL Mode
ACC_LYDIA = {}

if LYDIA_API_KEY:
    api_key = LYDIA_API_KEY
    api_client = API(api_key)
    lydia = LydiaAI(api_client)

@run_async
@typing_action
@register(pattern="^/autochat")
async def addcf(event):
    if event.fwd_from:
        return
    if event.is_group:
       if not (await is_register_admin(event.input_chat, event.message.sender_id)):
          await event.reply("")
          return
    reply_msg = await event.get_reply_message()
    sender = event.sender_id
    if reply_msg:
        session = lydia.create_session()
        session_id = session.id
        if reply_msg.from_id is None:
            return 
        if not reply_msg.from_id == sender:
            return 
        ACC_LYDIA.update({(event.chat_id & reply_msg.from_id): session})
        await event.reply("Auditor Enabled the use of AUTOCHAT for {} in chat: {}".format(str(reply_msg.from_id), str(event.chat_id)))
    else:
        return
@run_async
@typing_action
@register(pattern="^/stopchat")
async def remcf(event):
    if event.fwd_from:
        return
    if event.is_group:
       if not (await is_register_admin(event.input_chat, event.message.sender_id)):
          await event.reply("")
          return
    reply_msg = await event.get_reply_message()
    try:
        del ACC_LYDIA[event.chat_id & reply_msg.from_id]
        await event.reply("Auditor Enabled the use of AUTOCHAT for {} in chat: {}".format(str(reply_msg.from_id), str(event.chat_id)))
    except Exception:
        return

@register(pattern="")
async def user(event):
    user_text = event.text
    try:
        session = ACC_LYDIA[event.chat_id & event.from_id]
        msg = event.text
        text_rep = session.think_thought(msg)
        await event.reply(text_rep)
    except (KeyError, TypeError):
        return
