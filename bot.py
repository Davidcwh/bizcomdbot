import os
import telebot

from pairing import Pairing
from chats import Chats

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
pairing = Pairing(bot)
chats = Chats(bot)

# Angel & mortal pairing handlers --->
@bot.message_handler(commands=['start'], func=lambda message: True)
def start(message):
    pairing.start(message)

@bot.message_handler(commands=['startpoll'], func=lambda message: True)
def startpoll(message):
    pairing.startpoll(message)

@bot.message_handler(commands=['end'])
def end(message):
    pairing.end(message)

@bot.message_handler(commands=['generate'])
def generate(message):
    pairing_info = pairing.generate(message)
    if pairing_info is not None:
        chats.add_pairings(pairing_info)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    pairing.callback_query(call)


# Chat handlers --->
@bot.message_handler(commands=['a'])
def send_message_to_angel(message):
    if message.chat.type != 'private': # in case command is used in group chat
        return
    
    mortal_id = message.from_user.id
    if mortal_id not in chats.mortal_to_angel.keys():
        return

    message_for_angel = message.text[3:]
    chats.send_message_to_angel(message_for_angel, mortal_id)

@bot.message_handler(commands=['m'])
def send_message_to_mortal(message):
    if message.chat.type != 'private': # in case command is used in group chat
        return

    angel_id = message.from_user.id
    if angel_id not in chats.angel_to_mortal.keys():
        return

    message_for_mortal = message.text[3:]
    chats.send_message_to_mortal(message_for_mortal, angel_id)

@bot.message_handler(commands=['stopgame'])
def stopgame(message):
    if message.chat.type == 'private':
        return
    chats.stop_game(message.chat.id)
    

bot.infinity_polling()