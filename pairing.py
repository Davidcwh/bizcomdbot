import random

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException

# Encapsulates data and logic for handling A&M user registration + A&M pairing generation
class Pairing:
    def __init__(self, bot):
        self.bot = bot

        # stores info on group chats that are waiting for users to join A&M game
        # once the A&M pairings are generated for a group, the entry is removed
        # format: { chat_id : { user_id : username } }
        self.pending_groups = dict()

        # stores users who have started the @bizcomdbot
        # all users need to individual start the bot for A&M pairings to be generated
        # format: { user_id : chat_id } 
        self.joined_users = dict()

    # bot handler functions --->
    def start(self, message):
        if message.chat.type == 'private':
            self.joined_users[message.from_user.id] = message.chat.id
            self.bot.send_message(message.chat.id, "Hello! Thanks for starting the bot, pls wait for everyone in the group to join the poll :)")

    def startpoll(self, message):
        if message.chat.id in self.pending_groups.keys():
            # do nothing if there is already an ongoing poll
            return
        
        self.pending_groups[message.chat.id] = dict()
        self.bot.send_message(message.chat.id, self.generate_poll_text(message.chat.id), reply_markup=self.generate_options())
    
    def end(self, message):
        if message.chat.id not in self.pending_groups.keys():
            return
        
        self.pending_groups.pop(message.chat.id)
        self.bot.send_message(message.chat.id, "Previous poll ended! Press /startpoll to create a new one")

    # Steps for A&M pairing generation:
    # 1. Check for any users have not started the bot yet
    #       - if there is, send reminder message to group chat and return
    # 2. shuffle users to get random angel/mortal pairings
    # 3. send dm to angel about their mortal
    # 4. return dict of format { angel user id : mortal user id }
    def generate(self, message):
        if message.chat.id not in self.pending_groups.keys():
            return
        
        members = self.pending_groups[message.chat.id]
        id_list = []
        for id in members:
            id_list.append(id)

        # check if any users have not started the bot yet
        unjoined_users = self.get_unjoined_users(id_list)
        if len(unjoined_users) > 0:
            text = "Can't generate angel/mortal pairings yet, the following need to press \"start\" on @bizcomdbot tele bot:\n"
            for unjoined_id in unjoined_users:
                text += ("\n- @" + members[unjoined_id])

            text += "\n\nWhen done, press /generate again :)"
            self.bot.send_message(message.chat.id, text)
            return

         # generating angel - mortal pairings randomly
        random.shuffle(id_list)
        pairs = dict()
        for i in range(len(id_list)):
            angel = id_list[i]
            mortal = id_list[(i + 1) % len(id_list)] # wrap around to first user for last user
            pairs[angel] = mortal

        # send telegram DM to angels their respective mortals
        for angel_id in pairs.keys():
            mortal_id = pairs[angel_id]
            mortal_username = members[mortal_id]
            self.bot.send_message(angel_id, 'Hi! Your mortal is @' + mortal_username)

        self.pending_groups.pop(message.chat.id)
        self.bot.send_message(message.chat.id, "Angel - Mortal pairings generated! Angels should know their mortals now :)")

        return pairs
  
    # callback function for when the poll is updated with users joining/leaving game
    def callback_query(self, call):
        if call.message.chat.id not in self.pending_groups:
            return

        id = call.from_user.id
        username = call.from_user.username
        members = self.pending_groups[call.message.chat.id]

        if id in members.keys():
            members.pop(id)
        else:
            members[id] = username
        
        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                            text=self.generate_poll_text(call.message.chat.id), reply_markup=self.generate_options())    


    
    # helper functions --->
    def generate_poll_text(self, chat_id):
        text = "Join Bizcom D Angel & Mortal?\n\nFor those joining, pls also start the bot @bizcomdbot so you can receive updates on who your mortal is!\n\nPlaying:"
        members = self.pending_groups[chat_id]

        for id in members.keys():
            text += "\n"
            text += ("@" + members[id])
        return text

    def generate_options(self):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton("I'm in!", callback_data="modify members"))
        return markup

    def get_unjoined_users(self, id_list):
        unjoined_users = []
        for id in id_list:
            if id not in self.joined_users.keys() or self.has_user_deleted_bot(self.joined_users[id]):
                unjoined_users.append(id)

        return unjoined_users

    def has_user_deleted_bot(self, chat_id):
        try:
            self.bot.send_chat_action(chat_id=chat_id, action="typing") # used to see if user has active chat with bot
            return False
        except ApiTelegramException as e:
            # print(e)
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user':
                return True



