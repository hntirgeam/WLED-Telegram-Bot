import io
import logging
import os
from dataclasses import dataclass

from telegram import KeyboardButton, ParseMode, ReplyKeyboardMarkup, Update
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


@dataclass
class ResponseStrings:
    hello_text: str = "Use buttons to control WLED or send me a picture from which I will try to guess and set color"
    on_off: str = "LED is {}"
    done: str = "Done"
    current_mode: str = "Current mode is {}"
    guesed_color: str = "Looks like the color is... \n\n{}"
    error: str = "I dunno. Check... logs... or... is your WLED_URL correct..."


def start(update: Update, context: CallbackContext) -> None:
    buttons = [
        [KeyboardButton(ButtonStrings.on_off)],
        [KeyboardButton(ButtonStrings.br_down), KeyboardButton(ButtonStrings.br_up)],
        [KeyboardButton(ButtonStrings.random_mode)],
        [KeyboardButton(ButtonStrings.static_mode)],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ResponseStrings.hello_text,
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True),
    )


def message_handler(update: Update, context: CallbackContext):
    if ButtonStrings.on_off == update.message.text:
        res = utils.turn_off_on()
        response_text = ResponseStrings.on_off.format(res) if res else ResponseStrings.error
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    if ButtonStrings.br_up == update.message.text:
        res = utils.change_brightness(True)
        response_text = res if res else ResponseStrings.error
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    if ButtonStrings.br_down == update.message.text:
        res = utils.change_brightness(False)
        response_text = res if res else ResponseStrings.error
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    if ButtonStrings.random_mode == update.message.text:
        res = utils.set_random_mode()
        response_text = ResponseStrings.current_mode.format(res) if res else ResponseStrings.error
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    if ButtonStrings.static_mode == update.message.text:
        res = utils.set_static_mode()
        response_text = ResponseStrings.current_mode.format(res) if res else ResponseStrings.error
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)


def image_handler(update: Update, context: CallbackContext):
    file = update.message.photo[-1].file_id

    obj = context.bot.get_file(file)
    image = io.BytesIO()
    image = obj.download(out=image)

    color = utils.get_dominant_color_from_image(image)
    res = utils.set_dominant_color(color)
    if res:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ResponseStrings.guesed_color.format(res),
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=ResponseStrings.error)


updater = Updater(os.getenv("BOT_TOKEN"))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))

updater.start_polling()
