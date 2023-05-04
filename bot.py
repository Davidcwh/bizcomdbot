import os
import random

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

groups = dict() # stores chat_id -> member lists to support multiple chat groups

@bot.message_handler(commands=['start'], func=lambda message: True)
def start(message):
    if message.chat.id in groups.keys():
        # do nothing if there is already an ongoing poll
        return
    
    groups[message.chat.id] = dict()

    bot.send_message(message.chat.id, generatePollText(message.chat.id), reply_markup=generateOptions())

@bot.message_handler(commands=['end'])
def end(message):
    if message.chat.id not in groups.keys():
        return
    
    groups.pop(message.chat.id)
    bot.send_message(message.chat.id, "Previous poll ended! Press /start to create a new one")

@bot.message_handler(commands=['generate'])
def generate(message):
    if message.chat.id not in groups.keys():
        return
    
    # generating angel - mortal pairings randomly
    members = groups[message.chat.id]
    id_list = []
    for id in members:
        id_list.append(id)

    random.shuffle(id_list)

    pairs = dict()
    for i in range(len(id_list)):
        angel = id_list[i]
        mortal = id_list[(i + 1) % len(id_list)]
        pairs[angel] = mortal

    # send telegram DM to angels their respective mortals
    for angel_id in pairs.keys():
        mortal_id = pairs[angel_id]
        mortal_username = members[mortal_id]
        bot.send_message(angel_id, 'Hi! Your mortal is @' + mortal_username)

    groups.pop(message.chat.id)
    bot.send_message(message.chat.id, "Angel - Mortal pairings generated! Angels should know their mortals now :)")
    

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message.chat.id not in groups:
        return

    id = call.from_user.id
    username = call.from_user.username
    members = groups[call.message.chat.id]

    if id in members.keys():
        members.pop(id)
    else:
        members[id] = username
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=generatePollText(call.message.chat.id), reply_markup=generateOptions())    

def generatePollText(chat_id):
    text = "Join Bizcom D Angel & Mortal?\n\nPlaying:"
    members = groups[chat_id]

    for id in members.keys():
        text += "\n"
        text += members[id]
    return text

def generateOptions():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("I'm in!", callback_data="modify members"))
    return markup


bot.infinity_polling()