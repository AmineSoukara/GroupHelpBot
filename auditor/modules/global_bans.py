import html
import time
from datetime import datetime
from io import BytesIO
from typing import List

from telegram import Bot, Update, ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async
from telegram.utils.helpers import mention_html

import auditor.modules.sql.global_bans_sql as sql
from auditor import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, STRICT_GBAN, MESSAGE_DUMP, spamwtc
from auditor.modules.helper_funcs.chat_status import user_admin, is_user_admin, sudo_plus
from auditor.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from auditor.modules.helper_funcs.misc import send_to_list
from auditor.modules.sql.users_sql import get_all_chats

GBAN_ENFORCE_GROUP = 6

GBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to kick it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can kick group administrators",
    "Channel_private",
    "Not in the chat",
    "Can't remove chat owner",
}

UNGBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Method is available for supergroup and channel chats only",
    "Not in the chat",
    "Channel_private",
    "Chat_admin_required",
    "Peer_id_invalid",
    "User not found",
}


@run_async
@sudo_plus
def gban(update, context):  
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    banner = update.effective_user
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user or the ID specified is incorrect..")
        return

    if int(user_id) in SUDO_USERS:
        message.reply_text("I spy, with my little eye... a disaster! Why are you guys turning on each other?")
        return

    if int(user_id) in WHITELIST_USERS:
        message.reply_text("Wait Wait you want me to gban Whitelist user? Not in your Senses?")
        return

    if user_id == context.bot.id:
        message.reply_text("Fuckkkk")
        return

    try:
        user_chat = context.bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        else:
            return

    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return
    
    if not reason:
        message.reply_text("Global Ban must have a reason!")
        return

    full_reason = html.escape(
        f"{reason} // GBanned by {banner.first_name} id {banner.id}")

    if sql.is_user_gbanned(user_id):
        old_reason = sql.update_gban_reason(
            user_id, user_chat.username or user_chat.first_name,
            full_reason) or "None"
   
        old_reason = sql.update_gban_reason(user_id, user_chat.username or user_chat.first_name, reason)
        if old_reason:
            message.reply_text("This user is already gbanned.\n"
                               "I've gone and updated it with your new reason!".format(html.escape(old_reason)),
                               parse_mode=ParseMode.HTML)

        return

    message.reply_text(
        "<b>Initializing Global Ban</b>\n<b>Sudo Admin:</b> {}\n<b>User:</b> {}\n<b>ID:</b> <code>{}</code>\n<b>Reason:</b> {}"
        .format(mention_html(banner.id, banner.first_name),
                mention_html(user_chat.id, user_chat.first_name), user_chat.id,
                reason),
        parse_mode=ParseMode.HTML)

    if chat.type != 'private':
        chat_origin = "<b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)

    log_message = (f"<b>Global Ban</b>\n"
                   f"<b>Originated from:</b> {chat_origin}\n"
                   f"<b>Sudo Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
                   f"<b>ID:</b> {user_chat.id}\n"
                   f"<b>Reason:</b> {reason}")

    if MESSAGE_DUMP:
        try:
            log = context.bot.send_message(MESSAGE_DUMP, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = context.bot.send_message(MESSAGE_DUMP,
                                   log_message + "\n\nFormatting has been disabled due to an unexpected error.")

    else:
        send_to_list(bot, SUDO_USERS, html=True)

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, full_reason)
    
    message.reply_text("User is Succesfully Gbanned")
                       
    chats = get_all_chats()
    gbanned_chats = 0

    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            context.bot.kick_chat_member(chat_id, user_id)
            gbanned_chats += 1

        except BadRequest as excp:
            if excp.message in GBAN_ERRORS:
                pass
            else:
                message.reply_text(f"Could not gban due to: {excp.message}")
                if MESSAGE_DUMP:
                    context.bot.send_message(MESSAGE_DUMP, f"Could not gban due to {excp.message}",
                                     parse_mode=ParseMode.HTML)
                else:
                    send_to_list(bot, SUDO_USERS + SUPPORT_USERS, f"Could not gban due to: {excp.message}")
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    if MESSAGE_DUMP:
        log.edit_text(log_message, parse_mode=ParseMode.HTML)
    else:
        send_to_list(bot, SUDO_USERS + SUPPORT_USERS, f"Gban complete!")

    try:
        context.bot.send_message(user_id,
                         "You have been globally banned from all groups where I have administrative permissions."
                         f"If you think that this was a mistake, you may appeal your ban here: @ebruiser",
                         parse_mode=ParseMode.HTML)
    except:
        pass  # bot probably blocked by user


@run_async
@sudo_plus
def ungban(update, context):
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    banner = update.effective_user
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user or the ID specified is incorrect..")
        return

    user_chat = context.bot.get_chat(user_id)
    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if not sql.is_user_gbanned(user_id):
        message.reply_text("This user is not gbanned!")
        return

    if not reason:
        message.reply_text(
            "Removal of Global Ban requires a reason to do so, why not send me one?")
        return


    message.reply_text(
        "<b>Initializing Global Ban Removal</b>\n<b>Sudo Admin:</b> {}\n<b>User:</b> {}\n<b>ID:</b> <code>{}</code>\n<b>Reason:</b> {}"
        .format(mention_html(banner.id, banner.first_name),
                mention_html(user_chat.id, user_chat.first_name), user_chat.id,
                reason),
        parse_mode=ParseMode.HTML)

    if chat.type != 'private':
        chat_origin = f"<b>{html.escape(chat.title)} ({chat.id})</b>\n"
    else:
        chat_origin = f"<b>{chat.id}</b>\n"

    log_message = (f"<b>Global Ban Removal</b>\n"
                   f"<b>Originated from:</b> {chat_origin}\n"
                   f"<b>Sudo Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
                   f"<b>ID:</b> {user_chat.id}\n"
                   f"<b>Reason:</b> {reason}")
                  

    if MESSAGE_DUMP:
        try:
            log = context.bot.send_message(MESSAGE_DUMP, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = context.bot.send_message(MESSAGE_DUMP,
                                   log_message + "\n\nFormatting has been disabled due to an unexpected error.")
								   
    else:
        send_to_list(bot, SUDO_USERS + SUPPORT_USERS, log_message, html=True)

    chats = get_all_chats()
    ungbanned_chats = 0

    for chat in chats:
        chat_id = chat.chat_id

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            member = context.bot.get_chat_member(chat_id, user_id)
            if member.status == 'kicked':
                context.bot.unban_chat_member(chat_id, user_id)
                ungbanned_chats += 1

        except BadRequest as excp:
            if excp.message in UNGBAN_ERRORS:
                pass
            else:
                message.reply_text(f"Could not un-gban due to: {excp.message}")
                if MESSAGE_DUMP:
                    context.bot.send_message(MESSAGE_DUMP, f"Could not un-gban due to: {excp.message}",
                                     parse_mode=ParseMode.HTML)
                else:
                    context.bot.send_message(OWNER_ID, f"Could not un-gban due to: {excp.message}")
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    message.reply_text("This user have been ungbanned succesfully")

    
@run_async
@sudo_plus
def gbanlist(update, context):
    banned_users = sql.get_gban_list()

    if not banned_users:
        update.effective_message.reply_text(
            "There aren't any gbanned users! You're kinder than I expected...")
        return

    banfile = 'Gbanned users:\n'
    for user in banned_users:
        banfile += "[x] {} - {}\n".format(user["name"], user["user_id"])
        if user["reason"]:
            banfile += "Reason: {}\n".format(user["reason"])

    with BytesIO(str.encode(banfile)) as output:
        output.name = "gbanlist.txt"
        update.effective_message.reply_document(
            document=output,
            filename="gbanlist.txt",
            caption="Here is the list of currently gbanned users.")


@run_async
@sudo_plus
def ungban_quicc(update, context):
    args = context.args
    message = update.effective_message
    try:
        user_id = int(args[0])
    except Exception:
        return
    sql.ungban_user(user_id)
    message.reply_text(
        f"Yeety mighty your mom is gay, {user_id} have been ungbanned.")

   
def check_and_ban(update, user_id, should_message=True):

    try:
       spmban = spamwtc.get_ban(int(user_id))
       if spmban:
           update.effective_chat.kick_member(user_id)
           if should_message:
              update.effective_message.reply_text(
              f"This person has been detected as spambot by **SpamWatch** and has been removed!\nReason: <code>{spmban.reason}</code>",
              parse_mode=ParseMode.HTML)
              return
           else:
              return
    except Exception:
        pass

    if sql.is_user_gbanned(user_id):
        update.effective_chat.kick_member(user_id)
        if should_message:
            usr = sql.get_gbanned_user(user_id)
            greason = usr.reason
            if not greason:
                greason = "No reason given"

            update.effective_message.reply_text(f"*Alert! this user was GBanned and have been removed!*\n*Reason*: {greason}", parse_mode=ParseMode.MARKDOWN)
            return
                
@run_async
@sudo_plus
def enforce_gban(update, context):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    if sql.does_chat_gban(update.effective_chat.id) and update.effective_chat.get_member(context.bot.id).can_restrict_members:
        user = update.effective_user
        chat = update.effective_chat
        msg = update.effective_message

        if user and not is_user_admin(chat, user.id):
            check_and_ban(update, user.id)

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user
            if user and not is_user_admin(chat, user.id):
                check_and_ban(update, user.id, should_message=False)


@run_async
@user_admin
def antispam(update, context):
    args = context.args
    chat = update.effective_chat
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_antispam(chat.id)
            update.effective_message.reply_text("I've enabled gbans in this group. This will help protect you "
                                                "from spammers, unsavoury characters, and the biggest trolls.")
        elif args[0].lower() in ["off", "no"]:
            sql.disable_antispam(chat.id)
            update.effective_message.reply_text("I've disabled gbans in this group. GBans wont affect your users "
                                                "anymore. You'll be less protected from any trolls and spammers "
                                                "though!")
    else:
        update.effective_message.reply_text("Give me some arguments to choose a setting! on/off, yes/no!\n\n"
                                            "Your current setting is: {}\n"
                                            "When True, any gbans that happen will also happen in your group. "
                                            "When False, they won't, leaving you at the possible mercy of "
                                            "spammers".format(sql.does_chat_gban(chat.id)))
        
        
@run_async
@sudo_plus
def clear_gbans(update, context):
    banned = sql.get_gban_list()
    deleted = 0
    update.message.reply_text(
        "*Beginning to cleanup deleted users from global ban database...*\nThis process might take a while...",
        parse_mode=ParseMode.MARKDOWN)
    for user in banned:
        id = user["user_id"]
        time.sleep(0.1)  # Reduce floodwait
        try:
            context.bot.get_chat(id)
        except BadRequest:
            deleted += 1
            sql.ungban_user(id)
    update.message.reply_text("Done! {} deleted accounts were removed " \
    "from the gbanlist.".format(deleted), parse_mode=ParseMode.MARKDOWN)


def __stats__():
    return f"{sql.num_gbanned_users()} gbanned users."


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)

    text = "Globally banned: <b>{}</b>"
    if is_gbanned:
        text = text.format("Yes")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += f"\n<b>Reason:</b> {html.escape(user.reason)}"
        text += f"\n<b>Appeal Chat:</b> @ebruiser"
    else:
        text = text.format("No")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"This chat is enforcing *gbans*: `{sql.does_chat_gban(chat_id)}`."


__help__ = f"""
Antispam is used by the bot owners to ban spammers across all groups. This helps protect you and your groups by removing spam flooders as quickly as possible. This is enabled by default, but you can change this by using the command.\n
*Admin only:*\n
• /antispam <on/off/yes/no>: Change antispam security settings in the group, or return your current settings(when no arguments).\n
*What is SpamWatch?*\n
SpamWatch maintains a large constantly updated ban-list of spambots, trolls, bitcoin spammers and unsavoury characters.
lucifer will constantly help banning spammers off from your group automatically So, you don't have to worry about spammers storming your group.\n
Note: You can appeal gbans or ask gbans at @ebruiser
"""

GBAN_HANDLER = CommandHandler("gban", gban, pass_args=True)
UNGBAN_HANDLER = CommandHandler("ungban", ungban, pass_args=True)
GBAN_LIST = CommandHandler("gbanlist", gbanlist)

GBAN_STATUS = CommandHandler("antispam", antispam, pass_args=True, filters=Filters.group)
UNGBANQ_HANDLER = CommandHandler("ungban_quicc", ungban_quicc, pass_args=True)

GBAN_ENFORCER = MessageHandler(Filters.all & Filters.group, enforce_gban)
CLEAN_DELACC_HANDLER = CommandHandler("cleandelacc", clear_gbans)
                                      

dispatcher.add_handler(GBAN_HANDLER)
dispatcher.add_handler(UNGBAN_HANDLER)
dispatcher.add_handler(GBAN_LIST)
dispatcher.add_handler(GBAN_STATUS)
dispatcher.add_handler(CLEAN_DELACC_HANDLER)

__mod_name__ = "Gban⚙️"
__handlers__ = [GBAN_HANDLER, UNGBAN_HANDLER, GBAN_LIST, GBAN_STATUS]

if STRICT_GBAN:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
    __handlers__.append((GBAN_ENFORCER, GBAN_ENFORCE_GROUP))
