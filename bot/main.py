import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.database import Database
from utils.model import load_models
from utils.rating import Rating

from config.constants import main_characters, reaction
from config.exceptions import BotLogicError
from config.token import obtain_token

import logging
import traceback
# import src.inference as inference

bot = telebot.TeleBot(obtain_token())
db = Database("bot/data/db.csv")
rt_db = Rating("bot/data/rating.csv")
models = None

logging.basicConfig(
    filename='bot/data/bot.log',
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

    if choice in main_characters:
        bot.answer_callback_query(call.id, f"Бот будет говорить как: {choice}")
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id)

        reply = f"Бот будет говорить как: {choice}"
        bot.send_message(chat_id, text=reply, reply_to_message_id=msg_id)

        db.update(
            chat_id,
            character=choice,
            state="Talking"
        )

        logger.info(f"Replied to {chat_id} with:{reply}")
    elif choice in reaction:
        bot.answer_callback_query(
            call.id,
            f"Вы оценили предыдущее сообщение: {choice}"
        )
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id)

        data = db.get(chat_id)

        bot.send_message(
            chat_id,
            text="Мы можем продолжить диалог:)",
            reply_to_message_id=msg_id
        )

        rt_db.update(
            chat_id,
            data['prompt'],
            data['reply'],
            data['character'],
            choice
        )
        db.update(
            chat_id,
            state="Talking"
        )

        logger.info(f"Rated {data['reply']} with: {choice}")


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    logger.info(f"Got msg from {message.chat.id}:{message.text}")

    chat_id = message.chat.id
    msg_text = message.text
    data = db.get(chat_id)
    print(data)

    if data is None or data["state"] == "" or (
       data["state"] == "Talking" and msg_text == "/start"):

        reply_text = "Выберите героя, по образу которого будет говорить бот"

        bot.send_message(
            chat_id,
            reply_text,
            reply_markup=gen_markup(main_characters)
        )

        db.update(
            chat_id,
            character="",
            prompt="",
            reply="",
            state="ChooseCharacter"
        )
    elif data["state"] == "ChooseCharacter":
        reply_text = "Выберите героя в опросе выше"

        bot.send_message(
            chat_id,
            reply_text
        )
    elif data["state"] == "Talking":
        reply_text = models[data["character"]].get_reply(msg_text)

        bot.send_message(
            chat_id,
            reply_text
        )
        db.update(
            chat_id,
            prompt=msg_text,
            reply=reply_text,
            state="Talking"
        )

        reply_text = "Оцените качество фразы"

        bot.send_message(
            chat_id,
            reply_text,
            reply_markup=gen_markup(reaction)
        )
    else:
        logger.fatal("Unknown state")
        raise BotLogicError("Unknown state")


if __name__ == "__main__":
    try:
        models = load_models({
            'ФИБИ': "bot/models/Phoebe_mono_replics_cleaned",
            'ДЖОУИ': "",
            'МОНИКА': '',
            'РЕЙЧЕЛ': "",
            'РОСС': "",
            'ЧЕНДЛЕР': ''
        })
        while True:
            try:
                logger.info("start of session")
                bot.polling(none_stop=True)
            except Exception as e:
                logger.warning(f"Stopping the chat bot because of {e}")
                traceback.print_tb(e.__traceback__)
            finally:
                logger.debug("Flushing the db")
                db.flush()
                rt_db.flush()
                logger.debug("Flushed the db")
                logger.info("End of session")
    except KeyboardInterrupt:
        logger.debug("Flushing the db")
        db.flush()
        rt_db.flush()
        logger.debug("Flushed the db")
        logger.info("End of session")
