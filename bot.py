import os
import telebot

from pairing import Pairing

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
pairing = Pairing(bot)

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
    pairing.generate(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    pairing.callback_query(call)
    

bot.infinity_polling()