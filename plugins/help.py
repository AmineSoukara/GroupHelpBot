import logging
from Config import Messages as tr
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.private & filters.incoming & filters.command(['force']))
def _force(client, message):
    client.send_message(message.chat.id,
        text=tr.START_MSG.format(message.from_user.first_name, message.from_user.id),
        parse_mode="markdown",
        reply_to_message_id=message.message_id
        )


@Client.on_message(filters.private & filters.incoming & filters.command(['forcehelp']))
def _forcehelp(client, message):
    client.send_message(chat_id = message.chat.id,
        text = tr.HELP_MSG[1],
        parse_mode="markdown",
        disable_notification = True,
        reply_markup = InlineKeyboardMarkup(map(1)),
        reply_to_message_id = message.message_id
    )

forcehelp_callback_filter = filters.create(lambda _, __, query: query.data.startswith('forcehelp+'))

@Client.on_callback_query(forcehelp_callback_filter)
def forcehelp_answer(client, callback_query):
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    msg = int(callback_query.data.split('+')[1])
    client.edit_message_text(chat_id=chat_id,    message_id=message_id,
        text=tr.HELP_MSG[msg],    reply_markup=InlineKeyboardMarkup(map(msg))
    )



def map(pos):
    if(pos==1):
        button = [
            [InlineKeyboardButton(text = '-->', callback_data = "forcehelp+2")]
        ]
    elif(pos==len(tr.HELP_MSG)-1):
        url = "https://sushantgirdhar.github.io"
        button = [
            [InlineKeyboardButton(text = 'Support Chat', url="https://t.me/ebruiser")],
            [InlineKeyboardButton(text = 'Owner info', url=url)],
            [InlineKeyboardButton(text = '<--', callback_data = f"forcehelp+{pos-1}")]
        ]
    else:
        button = [
            [
                InlineKeyboardButton(text = '<--', callback_data = f"forcehelp+{pos-1}"),
                InlineKeyboardButton(text = '-->', callback_data = f"forcehelp+{pos+1}")
            ],
        ]
    return button
