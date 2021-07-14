import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.token import obtain_token
from utils.database import Database

import logging
# import src.inference as inference

TELEGRAM_API_TOKEN = obtain_token()
main_characters = ['ДЖОУИ', 'МОНИКА', 'РЕЙЧЕЛ', 'РОСС', 'ФИБИ', 'ЧЕНДЛЕР']
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
db = Database("bot/db.csv")

logging.basicConfig(
    filename='bot/bot.log', 
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
            InlineKeyboardButton(lst[2 * i], callback_data=f"cb_{lst[2 * i]}"), 
            InlineKeyboardButton(lst[2 * i + 1], callback_data=f"cb_{lst[2 * i + 1]}"), 
        )
    if but_count % 2 == 1:
        markup.add(
            InlineKeyboardButton(lst[but_count - 1], callback_data=f"cb_{lst[but_count - 1]}")
        )
    logger.debug(f"Generated keyboard markup")
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    choice = call.data[3:] if isinstance(call.data, str) else None
    chat_id = call.message.chat.id
    msg_id = call.message.id

    if choice is not None:
        bot.answer_callback_query(call.id, f"Bot will talk like: {choice}")
        db.update(chat_id, character=choice, state="Set_Character")
    
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id)
    reply = f"Бот будет говорить как: {choice}"
    bot.send_message(chat_id, text=reply, reply_to_message_id=msg_id)
    logger.info(f"Replied to {chat_id} with:{reply}")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    logger.info(f"Got msg from {message.chat.id}:{message.text}")
    msg = bot.send_message(message.chat.id, "Выберите героя, по образу которого будет говорить бот", reply_markup=gen_markup(main_characters))
    

if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except:
        print("Ok")
        db.flush()
        print("Ok")
