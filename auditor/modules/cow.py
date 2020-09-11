from telethon import events
from random import randrange
import io
import asyncio
import time
from auditor.events import register
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
        
import asyncio
from telethon import events
from cowpy import cow

@register(pattern=r"^/(\w+)say (.*)")
async def univsaye(cowmsg):
    if cowmsg.is_group:
     if not (await is_register_admin(cowmsg.input_chat, cowmsg.message.sender_id)):
          await cowmsg.reply("")
          return
    """ For .cowsay module, uniborg wrapper for cow which says things. """
    if not cowmsg.text[0].isalpha() and cowmsg.text[0] not in ("#", "@"):
        arg = cowmsg.pattern_match.group(1).lower()
        text = cowmsg.pattern_match.group(2)

        if arg == "cow":
            arg = "default"
        if arg not in cow.COWACTERS:
            return
        cheese = cow.get_cow(arg)
        cheese = cheese()

        await cowmsg.reply(f"`{cheese.milk(text).replace('`', '´')}`")
        
        
