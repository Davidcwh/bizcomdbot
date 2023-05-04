import os
import random

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

# stores chat_id -> member dict to support multiple chat groups
#               -> member dict stores user_id to username
groups = dict() 
joined_users = dict() # stores user_id -> chat_id

@bot.message_handler(commands=['start'], func=lambda message: True)
def start(message):
    if message.chat.type == 'private':
        joined_users[message.from_user.id] = message.chat.id
        bot.send_message(message.chat.id, "Hello! Thanks for starting the bot, pls wait for everyone in the group to join the poll :)")
     

@bot.message_handler(commands=['startpoll'], func=lambda message: True)
def startpoll(message):
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
    bot.send_message(message.chat.id, "Previous poll ended! Press /startpoll to create a new one")

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
    unjoined_users = getUnjoinedUsers(id_list)

    if len(unjoined_users) > 0:
        text = "Can't generate angel/mortal pairings yet, the following need to press \"\start\" on @bizcomdbot tele bot:\n"
        for unjoined_id in unjoined_users:
            text += ("\n- @" + members[unjoined_id])

        text += "\n\nWhen done, press /generate again :)"
        bot.send_message(message.chat.id, text)
        return

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
    text = "Join Bizcom D Angel & Mortal?\n\nFor those joining, pls also start the bot @bizcomdbot so you can receive updates on who your mortal is!\n\nPlaying:"
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

def getUnjoinedUsers(id_list):
    unjoined_users = []
    for id in id_list:
        if id not in joined_users.keys() or hasUserDeletedBot(joined_users[id]):
            unjoined_users.append(id)

    return unjoined_users

def hasUserDeletedBot(chat_id):
    try:
        bot.send_chat_action(chat_id=chat_id, action="typing") # used to see if user has active chat with bot
        return False
    except ApiTelegramException as e:
        # print(e)
        if e.result_json['description'] == 'Forbidden: bot was blocked by the user':
            return True


bot.infinity_polling()