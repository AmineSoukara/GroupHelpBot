import asyncio
import os
import random
import re
import shutil
import time
from html import unescape
from re import findall
from time import sleep
from urllib.error import HTTPError
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from telethon import events
from telethon import types
from telethon.tl import functions

from auditor import CHROME_DRIVER
from auditor import GOOGLE_CHROME_BIN
from auditor import LOGGER
from auditor import client
from auditor.events import register

CARBONLANG = "en"


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


@register(pattern="^/carbon (.*)")
async def carbon_api(e):
    user_id = e.message.sender_id
    chat_id = e.input_chat
    if e.is_group:
        if not (await is_register_admin(e.input_chat, e.message.sender_id)):
            return
    """ A Wrapper for carbon.now.sh """
    jj = "`Processing..`"
    gg = await e.reply(jj)
    CARBON = "https://carbon.now.sh/?bg=rgba(208%2C2%2C27%2C1)&t=night-owl&wt=none&l=htmlmixed&ds=true&dsyoff=20px&dsblur=68px&wc=true&wa=true&pv=56px&ph=56px&ln=false&fl=1&fm=Hack&fs=14px&lh=143%25&si=false&es=2x&wm=false&code={code}"
    global CARBONLANG
    code = e.pattern_match.group(1)
    await gg.edit("`Auditor Making Carbon..\n25%`")
    os.chdir("./")
    if os.path.isfile("./carbon.png"):
        os.remove("./carbon.png")
    url = CARBON.format(code=code, lang=CARBONLANG)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {"download.default_directory": "./"}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER,
                              options=chrome_options)
    driver.get(url)
    await gg.edit("`In Processing..\n50%`")
    download_path = "./"
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {
            "behavior": "allow",
            "downloadPath": download_path
        },
    }
    command_result = driver.execute("send_command", params)
    driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()
    await gg.edit("Lmao Almost Done..\n75%`")
    while not os.path.isfile("./carbon.png"):
        await asyncio.sleep(1)
    await gg.edit("`EbruiserSpace Uploading..\n100%`")
    file = "./carbon.png"
    await e.edit("`Uploading..`")
    await e.client.send_file(
        e.chat_id,
        file,
        caption="Made using [kek sushant](https://t.me/ebruiser),\
        \na project by [Ebruiser Labs](https://sushantgirdhar.github.io/)",
        force_document=True,
    )
    os.remove("./carbon.png")
    driver.quit()
