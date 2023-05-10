import random
from typing import List
from user import User
from user_storage import UserStorage
from group import Group
from group_storage import GroupStorage

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException    

# Encapsulates data and logic for handling A&M user registration + A&M pairing generation
class PairingEngine:
    def __init__(self, bot):
        self.bot = bot

        # stores info on group chats that are waiting for users to join A&M game
        # once the A&M pairings are generated for a group, the group is removed
        self.pending_groups = GroupStorage()

        # stores all users the bot has interacted with
        self.all_users = UserStorage()

        # stores users who have started the @bizcomdbot directly
        # all users need to individually start the bot for A&M pairings to be generated
        # user objects in started_users reference the same objects in all_users, 
        self.started_users = UserStorage()

    # bot handler functions --->
    def add_user(self, message):
        if not self.is_private_chat(message):
            return
        
        new_user = self.get_user_object(user_id=message.from_user.id, username=message.from_user.username)
        self.started_users.add_user(new_user)
        self.bot.send_message(message.chat.id, "Hello! Thanks for starting the bot, pls wait for everyone in the group to join the poll :)")
        print(new_user.username + " started the bot")

    def startpoll(self, message):
        if self.is_private_chat(message):
            return

        if self.pending_groups.contains_group(message.chat.id):
            # do nothing if there is already an ongoing poll
            return
        
        new_group = Group(message.chat.id)
        self.pending_groups.add_group(new_group)
        self.bot.send_message(message.chat.id, self.generate_poll_text(message.chat.id), reply_markup=self.generate_options())
    
    # callback function for when the poll is updated with users joining/leaving game
    def callback_query(self, call):
        if not self.pending_groups.contains_group(call.message.chat.id):
            return

        user_id = call.from_user.id
        username = call.from_user.username
        group = self.pending_groups.get_group(call.message.chat.id)

        if group.contains_user(user_id):
            group.remove_user(user_id)
        else:
            user = self.get_user_object(user_id=user_id, username=username)
            group.add_user(user)
        
        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                            text=self.generate_poll_text(call.message.chat.id), reply_markup=self.generate_options())   
    
    def end(self, message):
        if not self.pending_groups.contains_group(message.chat.id):
            return
        
        self.pending_groups.remove_group(message.chat.id)
        self.bot.send_message(message.chat.id, "Previous poll ended! Press /startpoll to create a new one")

    # Steps for A&M pairing generation:
    # 1. Check if any users have joined the poll
    # 2. Check if any users have not started the bot yet
    #       - if there is, send reminder message to group chat and return
    # 3. shuffle users to get random angel/mortal pairings
    # 4. send dm to angel about their mortal
    # 5. remove group from pending groups
    # 6. return group of users with angel and mortal assigned
    def generate(self, message) -> Group:
        if self.is_private_chat(message):
            return

        if not self.pending_groups.contains_group(message.chat.id):
            return
        
        group = self.pending_groups.get_group(message.chat.id)
        users = group.get_users_list()

        if len(users) == 0:
            self.bot.send_message(message.chat.id, "Can't start a game, no one has joined yet!\n\nWait till everyone has clicked \"I'm in!\" on the poll before pressing /generate again :)")
            return

        # check if any users have not started the bot yet
        not_started_users = self.get_not_started_users(users)
        if len(not_started_users) > 0:
            text = "Can't generate angel/mortal pairings yet, the following peeps need to start a private chat with the @bizcomdbot bot by pressing \"start\" or typing \"/start\":\n"
            for not_started_user in not_started_users:
                text += ("\n- " + not_started_user.username)

            text += "\n\nWhen done, press /generate again :)"
            self.bot.send_message(message.chat.id, text)
            return

        # generating angel - mortal pairings randomly
        random.shuffle(users)
        print("   angel   |  Mortal  ")
        for i in range(len(users)):
            angel_user = users[i]
            mortal_user = users[(i + 1) % len(users)] # wrap around to first user for last user
            angel_user.mortal = mortal_user
            mortal_user.angel = angel_user
            print(angel_user.username + "   |   " + mortal_user.username)

        # send telegram DM to angels their respective mortals
        generated_group = Group(message.chat.id)
        for user in users:
            self.send_mortal_info_to_user(user)
            generated_group.add_user(user)

        self.pending_groups.remove_group(message.chat.id)
        self.bot.send_message(message.chat.id, "Angel/Mortal pairings generated! Angels should know their mortals now :)")

        return generated_group
    
    # helper functions --->
    def get_user_object(self, user_id, username) -> User:
        if not self.all_users.contains_user(user_id):
            new_user = User(user_id=user_id, username=username)
            self.all_users.add_user(new_user)

        return self.all_users.get_user(user_id)

    def is_private_chat(self, message):
        return message.chat.type == 'private'

    def generate_poll_text(self, chat_id):
        text = "Join Bizcom D Angel & Mortal?\n\nFor those joining, pls also start a private chat with the bot @bizcomdbot so you can receive updates on who your mortal is!\n\nPlaying:"
        group = self.pending_groups.get_group(chat_id)
        user_id_to_object = group.users.users

        for user_id in user_id_to_object:
            text += "\n"
            text += user_id_to_object[user_id].username

        text += "\n\nWhen ready to play, press /generate :)"
        return text

    def generate_options(self):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton("I'm in!", callback_data="modify members"))
        return markup

    def get_not_started_users(self, users_list : List[User]) -> List[User]:
        not_started_users = []
        for user in users_list:
            user_id = user.user_id
            if not self.started_users.contains_user(user_id) or self.has_user_deleted_bot(user):
                not_started_users.append(user)

        return not_started_users

    def has_user_deleted_bot(self, user : User):
        chat_id = user.user_id
        try:
            self.bot.send_chat_action(chat_id=chat_id, action="typing") # used to see if user has active chat with bot
            return False
        except ApiTelegramException as e:
            # print(e)
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user':
                self.started_users.remove_user(user.user_id)
                print(user.username + " deleted the bot")
                return True
            
    def send_mortal_info_to_user(self, user : User):
        mortal_user = user.mortal
        self.bot.send_message(user.user_id, 'Hi! Your mortal is ' + mortal_user.username)

        angel_chat_instructions = "To chat with your angel, send messages prefixed with \"/a\" command.\nFor example: \"/a hello angel who you\""
        mortal_chat_instructions = "To chat with your mortal, send messages prefixed with \"/m\" command.\nFor example: \"/m hello mortal guess who am i\""
        chat_instructions = angel_chat_instructions + "\n\n" + mortal_chat_instructions
        self.bot.send_message(user.user_id, chat_instructions)
