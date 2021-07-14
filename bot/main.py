import telebot
import string
import requests
import os
import glob
from telebot import types
import importlib
# import src.inference as inference

TELEGRAM_API_TOKEN = "secret"

TEXT_FOLDER = "texts"
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
# model = inference.InferenceModel()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_monika = types.KeyboardButton("Моника")
    button_chandler = types.KeyboardButton("Чендлер")
    button_phoebe = types.KeyboardButton("Фиби")
    button_joye = types.KeyboardButton("Джоуи")
    button_ross = types.KeyboardButton("Росс")
    button_rachel = types.KeyboardButton("Рейчел")
    keyboard.add(button_monika)
    keyboard.add(button_chandler)
    keyboard.add(button_phoebe)
    keyboard.add(button_joye)
    keyboard.add(button_ross)
    keyboard.add(button_rachel)
    bot.reply_to(message, f'Я бот. Приятно познакомиться, {message.from_user.first_name}!\n Здесь ты можешь'
                          f' пообщаться с одним из героев сериала \"Друзья\". Выбери, с кем бы ты хотел поговорить.',
                 reply_markup=keyboard)





# @bot.message_handler(commands=['reload_model'])
# def sst_request(message):
#     importlib.reload(inference)
#     model = inference.InferenceModel()
#     bot.reply_to(message, f'{message.from_user.first_name}, успех, модель перезагружена из checkpoint {model.checkpoint_path}')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    mod_message = message.text.lower()
    mod_message = mod_message.translate(str.maketrans('','', string.punctuation))
    if mod_message == 'моника':
        pass
        # bot.send_message(message.from_user.id, 'Привет!')
    else:
        pass
        # bot.send_message(message.from_user.id, 'Не понимаю, что это значит.')


# @bot.message_handler(content_types=['voice'])
# def voice_processing(message):
#     file_info = bot.get_file(message.voice.file_id)
#     file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TELEGRAM_API_TOKEN, file_info.file_path))
#     user_name = message.from_user.username
#     user_folder = os.path.join(AUDIO_FOLDER, user_name)
#     if not os.path.isdir(user_folder):
#         os.mkdir(user_folder)
#
#     if not os.listdir(user_folder):
#         new_id = 0
#     else:
#         files = glob.glob(os.path.join(user_folder, "*"))
#         latest_file = max(files, key=os.path.getctime)
#         new_id = int(os.path.splitext(os.path.basename(latest_file))[0]) + 1
#
#     filename = os.path.join(user_folder, f"{new_id}.ogg")
#     with open(filename, "wb+") as f:
#         f.write(file.content)
#     # text = model.run(os.path.abspath(filename))
#     user_folder = os.path.join(TEXT_FOLDER, user_name)
#     if not os.path.isdir(user_folder):
#         os.mkdir(user_folder)
#
#     if not os.listdir(user_folder):
#         new_id = 0
#     else:
#         files = glob.glob(os.path.join(user_folder, "*"))
#         latest_file = max(files, key=os.path.getctime)
#         new_id = int(os.path.splitext(os.path.basename(latest_file))[0]) + 1
#
#     filename = os.path.join(user_folder, f"{new_id}.txt")
#     with open(filename, "w+") as f:
#         f.write(text)
#         f.write("\n")
#     bot.send_message(message.from_user.id, f'Распознанный текст: {text}.')


if __name__ == "__main__":

    bot.polling(none_stop=True)

