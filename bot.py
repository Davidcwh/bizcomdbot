import os
import telebot

from pairing_engine import PairingEngine
from chat_engine import ChatEngine

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
pairing = PairingEngine(bot)
chats = ChatEngine(bot)

# Angel & mortal pairing handlers --->
@bot.message_handler(commands=['start'], func=lambda message: True)
def add_user(message):
    pairing.add_user(message)

@bot.message_handler(commands=['startpoll'], func=lambda message: True)
def startpoll(message):
    pairing.startpoll(message)

@bot.message_handler(commands=['endpoll'])
def end(message):
    pairing.end(message)

@bot.message_handler(commands=['generate'])
def generate(message):
    generated_group = pairing.generate(message)
    if generated_group is not None:
        chats.add_group(generated_group)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    pairing.callback_query(call)


# Chat handlers --->
@bot.message_handler(commands=['a'])
def send_message_to_angel(message):
    if message.chat.type != 'private': # in case command is used in group chat
        return
    
    message_for_angel = message.text[3:]
    chats.send_message_to_angel(message_for_angel, message.from_user.id)

@bot.message_handler(commands=['m'])
def send_message_to_mortal(message):
    if message.chat.type != 'private': # in case command is used in group chat
        return

    message_for_mortal = message.text[3:]
    chats.send_message_to_mortal(message_for_mortal, message.from_user.id)

@bot.message_handler(commands=['stopgame'])
def stopgame(message):
    if message.chat.type == 'private':
        return
    chats.stop_game(message.chat.id)
    

bot.infinity_polling()