# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import sqlite3
import requests

text = ''
type = ''
caption = ''
id = ''
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

admin = 'cryptobroker_x'

TOKEN = '6695923427:AAFzytGws8yftOwnyUI6DpUhqoyKWmzs'

KNOPKA1 = 'Кнопка 1'
KNOPKA2 = 'Кнопка 2'
KNOPKA3 = 'Кнопка 3'
KNOPKA4 = 'Кнопка 4'

TEXT1 = 'Это кнопка номер 1 😎'
TEXT2 = 'Это кнопка номер 2 😎'
TEXT3 = 'Это кнопка номер 3 😎'
TEXT4 = 'Это кнопка номер 4 😎'

bot = telebot.TeleBot(TOKEN)

###################### СООБЩЕНИЕ ПОСЛЕ ПОДАЧИ ЗАЯВКИ ######################

@bot.chat_join_request_handler()
def new_start(message: telebot.types.ChatJoinRequest):
    btn1 = KeyboardButton(KNOPKA1)
    btn2 = KeyboardButton(KNOPKA2)
    btn3 = KeyboardButton(KNOPKA3)
    btn4 = KeyboardButton(KNOPKA4)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1).add(btn2).add(btn3).add(btn4)

    bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}. Твоя заявка принята!", parse_mode= 'Markdown', reply_markup = keyboard)
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)

    cursor.execute(f"""SELECT user_id FROM Users WHERE user_id=:user""",  {'user': message.from_user.id})
    username = cursor.fetchone()
    conn.commit()
    
    if username is None:
        cursor.execute('INSERT INTO Users (user_id, username) VALUES (?, ?)', (message.from_user.id, message.from_user.username,))
        conn.commit()



###################### БЛОК РАССЫЛКИ ######################

@bot.message_handler(commands = ['send'])
def msg_send(message):
    if message.from_user.username == admin:
        btn1 = KeyboardButton("Текст")
        btn2 = KeyboardButton("Фото")
        btn3 = KeyboardButton("Голосовое")
        btn5 = KeyboardButton("Отмена")
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1).add(btn2).add(btn3).add(btn5)
        bot.send_message(message.from_user.id, 'Выберите тип отправляемого медиа:', parse_mode= 'Markdown', reply_markup = keyboard)
        bot.register_next_step_handler(message, upload_send)
    else:
        bot.send_message(message.from_user.id, f'Вы не админ')

def upload_send(message):

    if message.text == 'Фото':
        bot.send_message(message.from_user.id, 'Пришлите фото, можно с описанием', parse_mode= 'Markdown')
        bot.register_next_step_handler(message, photo)
    elif message.text == "Текст":
        bot.send_message(message.from_user.id, 'Пришлите текст', parse_mode= 'Markdown')
        bot.register_next_step_handler(message, text_msg)
    elif message.text == 'Голосовое':
        bot.send_message(message.from_user.id, 'Пришлите голосовое сообщение', parse_mode= 'Markdown')
        bot.register_next_step_handler(message, voice)
    else:
        start(message)

def text_msg(message):
    """Функция отправки текста"""

    global type, text
    type = 'text'
    text = message.text

    btn1 = KeyboardButton('Да')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1)

    bot.send_message(message.from_user.id, f"Подтвердите отправку сообщения всем подписчикам: \n\nОтсылаем: {type}", parse_mode= 'Markdown', reply_markup = keyboard)
    bot.register_next_step_handler(message, sender)

def photo(message):
    """Функция отправки фото"""

    global type, caption
    type = 'photo'
    caption = message.caption

    fileID = message.photo[-1].file_id   
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)

    btn1 = KeyboardButton('Да')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1)

    bot.send_message(message.from_user.id, f"Подтвердите отправку сообщения всем подписчикам: \n\nОтсылаем: {type}", parse_mode= 'Markdown', reply_markup = keyboard)
    bot.register_next_step_handler(message, sender)

def voice(message):
    """Функция отправки гс"""

    global type
    type = 'voice'

    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))

    with open('voice.ogg','wb') as f:
        f.write(file.content)

    btn1 = KeyboardButton('Да')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1)

    bot.send_message(message.from_user.id, f"Подтвердите отправку сообщения всем подписчикам: \n\nОтсылаем: {type}", parse_mode= 'Markdown', reply_markup = keyboard)
    bot.register_next_step_handler(message, sender)


def sender(message):
    global text, type, caption, id

    if message.text == 'Да':
        cursor.execute(f"""SELECT user_id FROM Users""")
        all_ids = cursor.fetchall()

        count = 0

        try:
            for id in all_ids:
                if id[0]:
                    try:      
                        if type == 'photo':
                            new_file = open('image.jpg', 'rb')
                            bot.send_photo(id[0], photo=new_file, caption=caption, parse_mode='html')
                        elif type == 'voice':
                            f = open('voice.ogg', 'rb')
                            bot.send_voice(id[0], f)
                        elif type == 'text':
                            bot.send_message(id[0], text, parse_mode='html')
                        count += 1
                    except:
                        pass
        except Exception as e:
            print(e)

        bot.send_message(message.from_user.id, f'Рассылка успешна закончена, всего получателей: {count}', parse_mode= 'Markdown')
        start(message)
    else:
        bot.send_message(message.from_user.id, f'Рассылка отменена.')



###################### ОТВЕТЫ ПО КНОПКАМ ######################

@bot.message_handler(content_types='text')
def message_reply(message):

    if message.text == KNOPKA1:
        bot.send_message(message.from_user.id, TEXT1, parse_mode= 'Markdown')

    if message.text == KNOPKA2:
        bot.send_message(message.from_user.id, TEXT2, parse_mode= 'Markdown')

    if message.text == KNOPKA3:
        bot.send_message(message.from_user.id, TEXT3, parse_mode= 'Markdown')

    if message.text == KNOPKA4:
        bot.send_message(message.from_user.id, TEXT4, parse_mode= 'Markdown')


def start(message):
    btn1 = KeyboardButton(KNOPKA1)
    btn2 = KeyboardButton(KNOPKA2)
    btn3 = KeyboardButton(KNOPKA3)
    btn4 = KeyboardButton(KNOPKA4)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1).add(btn2).add(btn3).add(btn4)

    bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}. Ты в главном меню.", parse_mode= 'Markdown', reply_markup = keyboard)




while True:
    try:
        bot.infinity_polling(allowed_updates = telebot.util.update_types)
    except:
        continue