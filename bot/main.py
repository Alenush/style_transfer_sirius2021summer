import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import logging
import traceback

from utils.database import Database
from utils.rating import Rating

from utils.model import load_models

from ui.constants import TOKEN, main_characters, reaction, greeting

import json
import numpy as np
import requests
from time import sleep

bot = telebot.TeleBot(TOKEN)
db = Database("data/db.csv")
rt_db = Rating("data/rating.csv")
NO_MODEL = ""
DEBUG_MODELS = {
    'ФИБИ': NO_MODEL,
    'ДЖОУИ': NO_MODEL,
    'МОНИКА': NO_MODEL,
    'РЕЙЧЕЛ': NO_MODEL,
    'РОСС': NO_MODEL,
    'ЧЕНДЛЕР': NO_MODEL
}
models = None

logging.basicConfig(
    filename='data/bot.log',
    format='%(name)s %(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    encoding='utf-8',
    level=logging.DEBUG)
# model = inference.InferenceModel()
logger = logging.getLogger("bot")


def gen_markup(lst: list):
    logger.debug(f"Generating keyboard markup from {str(lst)}")

    markup = InlineKeyboardMarkup()
    markup.row_width = 2

    but_count = len(lst)

    for i in range(but_count // 2):
        markup.add(
            InlineKeyboardButton(
                lst[2 * i],
                callback_data=f"cb_{lst[2 * i]}"
            ),
            InlineKeyboardButton(
                lst[2 * i + 1],
                callback_data=f"cb_{lst[2 * i + 1]}"
            ),
        )

    if but_count % 2 == 1:
        markup.add(
            InlineKeyboardButton(
                lst[but_count - 1],
                callback_data=f"cb_{lst[but_count - 1]}"
            )
        )

    logger.debug("Generated keyboard markup")
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    choice = call.data[3:] if isinstance(call.data, str) else None
    chat_id = call.message.chat.id
    msg_id = call.message.id

    logger.debug(f"Callback handler called with {choice} from {chat_id}")

    if choice in main_characters:
        bot.answer_callback_query(call.id, f"Бот будет говорить как: {choice}")
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id)
        bot.edit_message_text(
            f"Сейчас скажу что-нибудь, как {choice}...",
            chat_id, msg_id)
        reply = models[choice].get_reply("Привет!")
        bot.edit_message_text(
            reply,
            chat_id, msg_id)
        bot.edit_message_reply_markup(
            chat_id=chat_id, message_id=msg_id,
            reply_markup=gen_markup(reaction))

        db.update(
            chat_id,
            data={
                'character': choice,
                'prompt': "Привет!",
                "reply": reply
            }
        )

        logger.info(f"Set character in {chat_id} to {choice}")
    elif choice in reaction:
        bot.answer_callback_query(
            call.id,
            f"Вы оценили предыдущее сообщение: {choice}"
        )
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id)

        data = db.get(chat_id)

        rt_db.append(
            chat_id,
            data['prompt'],
            data['reply'],
            data['character'],
            choice
        )

        logger.info(f"Rated reply {data['reply']} for " +
                    f"{data['prompt']} with: {choice}")


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    logger.info(f"Got msg from {message.chat.id}:{message.text}")

    chat_id = message.chat.id
    msg_text = message.text
    data = db.get(chat_id)

    flag_start = (data is not None) and (not isinstance(
        data["character"], str)) and np.isnan(data["character"])

    if msg_text in ["/start", "/help"] or data is None:
        bot.send_message(
            chat_id,
            greeting.format(message.from_user.first_name)
        )

        db.initialize(chat_id=chat_id)
    elif msg_text == "/change" or flag_start:

        reply_text = "Выберите героя, по образу которого будет говорить бот"

        bot.send_message(
            chat_id,
            reply_text,
            reply_markup=gen_markup(main_characters)
        )

        db.initialize(chat_id=chat_id)

        logger.info(f"Request from {chat_id} to change character")
    else:
        character = data["character"]
        msg_id = bot.send_message(
            chat_id,
            f"Сейчас скажу что-нибудь, как {character}..."
        ).message_id

        logger.info(f"Generated text for {chat_id} for {character}")

        reply_text = models[character].get_reply(msg_text)
        bot.edit_message_text(reply_text, chat_id, msg_id)
        bot.edit_message_reply_markup(
            chat_id=chat_id, message_id=msg_id,
            reply_markup=gen_markup(reaction))
        db.update(
            chat_id,
            data={
                'prompt': msg_text,
                'reply': reply_text
            }
        )


if __name__ == "__main__":

    with open("data/models.json", encoding="utf-8") as f:
        models_paths = json.load(f)

    models = load_models(models_paths) # DEBUG_MODELS
    try:
        logger.info("start of session")
        while True:
            try:
                bot.polling(none_stop=True)
            except requests.exceptions.ConnectionError:
                sleep(1)
    except Exception as e:
        logger.warning(f"Stopping the chat bot because of {e}")
        traceback.print_tb(e.__traceback__)
        print(e)
    except KeyboardInterrupt:
        logger.warning("Stopping the chat bot because of kill")
    finally:
        logger.debug("Flushing the db")
        db.flush()
        rt_db.flush()
        logger.debug("Flushed the db")
        logger.info("End of session")
