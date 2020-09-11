import io
import textwrap
from PIL import Image, ImageDraw, ImageFont
from auditor.events import register
import random
from auditor import LOGGER, client
from telethon import types
from telethon.tl import functions

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


from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.errors.rpcerrorlist import (UserIdInvalidError, MessageTooLongError, ChatAdminRequiredError)
                                                                                    
@register(pattern="^/users$")
async def get_users(show):
        if not show.is_group:
            await show.reply("Are you sure this is a group?")
            return
        if show.is_group:
         if not (await is_register_admin(show.input_chat, show.message.sender_id)):
          await show.reply("")
          return
        info = await show.client.get_entity(show.chat_id)
        title = info.title if info.title else "this chat"
        mentions = "Users in {}: \n".format(title)
        async for user in show.client.iter_participants(show.chat_id):
                  if not user.deleted:
                     mentions += f"\n[{user.first_name}](tg://user?id={user.id}) {user.id}"
                  else:
                      mentions += f"\nDeleted Account {user.id}"
        file = open("userslist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
                show.chat_id,
                "userslist.txt",
                caption='Users in {}'.format(title),
                reply_to=show.id,
                )
        os.remove("userslist.txt")
