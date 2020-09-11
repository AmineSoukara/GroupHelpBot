from io import BytesIO
from time import sleep
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from auditor.modules.helper_funcs.chat_status import is_user_ban_protected, sudo_plus

import auditor.modules.sql.users_sql as sql
from auditor.modules.sql.users_sql import get_all_users
from auditor import dispatcher, OWNER_ID, LOGGER, SUDO_USERS, WHITELIST_USERS
from auditor.modules.helper_funcs.filters import CustomFilters

USERS_GROUP = 4
CHAT_GROUP = 10


@run_async
@sudo_plus
def quickscope(update, context):
    args = context.args
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        context.bot.kick_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted banning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
@sudo_plus
def quickunban(update, context):
    args = context.args
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        context.bot.unban_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted unbanning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
@sudo_plus
def banall(update, context):
    args = context.args
    if args:
        chat_id = str(args[0])
        all_mems = sql.get_chat_members(chat_id)
    else:
        chat_id = str(update.effective_chat.id)
        all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            context.bot.kick_chat_member(chat_id, mems.user)
            update.effective_message.reply_text("Tried banning " + str(mems.user))
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(excp.message + " " + str(mems.user))
            continue


@run_async
@sudo_plus
def snipe(update, context):
    args = context.args
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            context.bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text("Couldn't send the message. Perhaps I'm not part of that group?")
            
   

  
@run_async
@sudo_plus
def msgtoall(update, context):

    to_send = update.effective_message.text.split(None, 1)

    if len(to_send) >= 2:
        users = get_all_users()
        failed_user = 0
        for user in users:
            try:
                context.bot.sendMessage(int(user.user_id), to_send[1])
                sleep(0.1)
            except TelegramError:
                failed_user += 1
                LOGGER.warning("Couldn't send broadcast to %s", str(user.user_id))

        update.effective_message.reply_text(
            f"Broadcast complete. {failed_user} failed to receive message, probably due to being blocked"
            )       
        
SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True)
BANALL_HANDLER = CommandHandler("banall", banall, pass_args=True)
QUICKSCOPE_HANDLER = CommandHandler("quickscope", quickscope, pass_args=True)
QUICKUNBAN_HANDLER = CommandHandler("quickunban", quickunban, pass_args=True)
MSGTOALL_HANDLER = CommandHandler("msgtoall", msgtoall)

dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(BANALL_HANDLER)
dispatcher.add_handler(QUICKSCOPE_HANDLER)
dispatcher.add_handler(QUICKUNBAN_HANDLER)
dispatcher.add_handler(MSGTOALL_HANDLER)
