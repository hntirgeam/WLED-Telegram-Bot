import logging
import os
from dataclasses import dataclass

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

import utils

logger_debug = logging.getLogger("log_debug")
logger_info = logging.getLogger("log_info")


@dataclass
class ButtonStrings:
    on_off: str = "On/Off"
    br_up: str = "Brightness +"
    br_down: str = "Brightness -"
    random_mode: str = "Random mode"
    static_mode: str = "Static mode"


def start(update: Update, context: CallbackContext) -> None:
    buttons = [
        [KeyboardButton(ButtonStrings.on_off)],
        [KeyboardButton(ButtonStrings.br_down), KeyboardButton(ButtonStrings.br_up)],
        [KeyboardButton(ButtonStrings.random_mode)],
        [KeyboardButton(ButtonStrings.static_mode)],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Let's gooooo!",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True),
    )


def messageHandler(update: Update, context: CallbackContext):
    if ButtonStrings.on_off == update.message.text:
        res = utils.turn_off_on()
        if res:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Done")

    if ButtonStrings.br_up == update.message.text:
        res = utils.change_brightness(True)
        if res:
            context.bot.send_message(chat_id=update.effective_chat.id, text=res)

    if ButtonStrings.br_down == update.message.text:
        res = utils.change_brightness(False)
        if res:
            context.bot.send_message(chat_id=update.effective_chat.id, text=res)

    if ButtonStrings.random_mode == update.message.text:
        res = utils.random_mode()
        if res:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Current mode is "{res}"')

    if ButtonStrings.static_mode == update.message.text:
        res = utils.static_mode()
        if res:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Current mode is "{res}"')


updater = Updater(os.getenv("BOT_TOKEN"))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text, messageHandler))

updater.start_polling()
