import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.database import Database
from utils.exceptions import BotLogicError
from utils.token import obtain_token
from utils.model import load_models

import logging
# import src.inference as inference

TELEGRAM_API_TOKEN = obtain_token()
main_characters = ['ДЖОУИ', 'МОНИКА', 'РЕЙЧЕЛ', 'РОСС', 'ФИБИ', 'ЧЕНДЛЕР']
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
db = Database("bot/data/db.csv")
models = load_models({
    'ФИБИ': "../gdrive/MyDrive/Style_Transfer_Models/gpt_large/mono/Phoebe_large_mono/"
})

logging.basicConfig(
    filename='bot/data/bot.log',
    format='%(name)s %(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
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

    if choice is not None:
        bot.answer_callback_query(call.id, f"Bot will talk like: {choice}")
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id)
        reply = f"Бот будет говорить как: {choice}"
        msg = bot.send_message(chat_id, text=reply, reply_to_message_id=msg_id)
        db.update(
            chat_id,
            character=choice,
            last_msg=reply,
            last_sent_msg_id=msg.message_id,
            state="SetCharacter"
        )
        logger.info(f"Replied to {chat_id} with:{reply}")


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    logger.info(f"Got msg from {message.chat.id}:{message.text}")

    chat_id = message.chat.id
    msg_text = message.text
    data = db.get(chat_id)

    if data["state"] == "" or (
       data["state"] == "Talking" and msg_text == "/change_hero"):

        reply_text = "Выберите героя, по образу которого будет говорить бот"

        msg = bot.send_message(
            chat_id,
            reply_text,
            reply_markup=gen_markup(main_characters)
        )
        db.update(
            chat_id,
            character="",
            last_msg=reply_text,
            last_sent_msg_id=msg.message_id,
            state="ChooseCharacter"
        )
    elif data["state"] == "ChooseCharacter":
        reply_text = "Выберите героя в опросе выше"

        msg = bot.send_message(
            chat_id,
            reply_text
        )
        db.update(
            chat_id,
            character="",
            last_msg=reply_text,
            last_sent_msg_id=msg.message_id,
            state="ChooseCharacter"
        )
    elif data["state"] == "SetCharacter":
        reply_text = f"Привет, я {data['character']}. Давай общаться?"

        msg = bot.send_message(
            chat_id,
            reply_text
        )
        db.update(
            chat_id,
            character="",
            last_msg=reply_text,
            last_sent_msg_id=msg.message_id,
            state="Talking"
        )
    elif data["state"] == "Talking":
        reply_text = models[data["character"]].get_reply(msg_text)

        msg = bot.send_message(
            chat_id,
            reply_text
        )
        db.update(
            chat_id,
            character="",
            last_msg=reply_text,
            last_sent_msg_id=msg.message_id,
            state="Talking"
        )

        reply_text = "Оцените качество фразы"

        msg = bot.send_message(
            chat_id,
            reply_text,
            reply_markup=gen_markup(["👎", "👍"])
        )
        db.update(
            chat_id,
            character="",
            last_msg=reply_text,
            last_sent_msg_id=msg.message_id,
            state="Talking"
        )
    else:
        logger.fatal("Unknown state")
        raise BotLogicError("Unknown state")


if __name__ == "__main__":
    logger.info("start of session")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.warning(f"Stopping the chat bot because of {e}")
    finally:
        logger.debug("Flushing the db")
        db.flush()
        logger.debug("Flushed the db")
        logger.info("End of session")
