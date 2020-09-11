from telethon import events
from random import randrange
import io
import asyncio
import time
from auditor.events import register
import glob
import os
import spotdl, subprocess
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


@register(pattern="^/news")
async def _(event):
  if event.is_group:
     return
  if event.fwd_from:
     return
 
  news_url="https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
  Client=urlopen(news_url)
  xml_page=Client.read()
  Client.close()
  soup_page=soup(xml_page,"xml")
  news_list=soup_page.findAll("item")
  for news in news_list:
       title = news.title.text
       text = news.link.text
       date = news.pubDate.text
       seperator = "-"*50
       l = "\n"
       lastisthis = title+l+text+l+date+l+seperator
       await event.reply(lastisthis)


from telethon.tl.types import InputMediaDice


@register(pattern="^/basketball")
async def _(event):
    if event.fwd_from:
        return
    if event.is_group:
     if not (await is_register_admin(event.input_chat, event.message.sender_id)):
          await event.reply("")
          return
    input_str = print(randrange(6))
    r = await event.reply(file=InputMediaDice('🏀'))
    if input_str:
        try:
            required_number = int(input_str)
            while not r.media.value == required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice('🏀'))
        except:
            pass


@register(pattern="^/dart")
async def _(event):
    if event.fwd_from:
        return
    if event.is_group:
     if not (await is_register_admin(event.input_chat, event.message.sender_id)):
          await event.reply("")
          return
    input_str = print(randrange(7))
    r = await event.reply(file=InputMediaDice('🎯'))
    if input_str:
        try:
            required_number = int(input_str)
            while not r.media.value == required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice('🎯'))
        except:
            pass
