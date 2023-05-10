from group_storage import GroupStorage
from group import Group
from user_storage import UserStorage
from user import User

from telebot.apihelper import ApiTelegramException

class ChatEngine:
    def __init__(self, bot):
        self.bot = bot

        self.ongoing_groups = GroupStorage()
        self.chatting_users = UserStorage()
    
    def add_group(self, group : Group):
        self.ongoing_groups.add_group(group)
        users_list = group.get_users_list()
        for user in users_list:
            self.chatting_users.add_user(user)

    def send_message_to_angel(self, message, user_id):
        if not self.chatting_users.contains_user(user_id) or message == "":
            return
        
        user = self.chatting_users.get_user(user_id)
        angel_user = user.angel

        message = "Your mortal: " + message

        try:
            self.bot.send_message(angel_user.user_id, message)
        except ApiTelegramException as e:
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user': 
                self.bot.send_message(user.user_id, "Oops looks like your angel deleted the chat with the bot, can't send them messages :/")


    def send_message_to_mortal(self, message, user_id):
        if not self.chatting_users.contains_user(user_id) or message == "":
            return
        
        user = self.chatting_users.get_user(user_id)
        mortal_user = user.mortal
        
        message = "Your angel: " + message

        try:
            self.bot.send_message(mortal_user.user_id, message)
        except ApiTelegramException as e:
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user': 
                self.bot.send_message(user.user_id, "Oops looks like your mortal deleted the chat with the bot, can't send them messages :/")

    def stop_game(self, group_chat_id):
        if not self.ongoing_groups.contains_group(group_chat_id):
            self.bot.send_message(group_chat_id, "There's no existing Angel & Mortal game for this group chat!")
            return
        
        group = self.ongoing_groups.get_group(group_chat_id)
        users_list = group.get_users_list()

        for user in users_list:
            user.resetAngelMortal()
            self.chatting_users.remove_user(user.user_id)
        
        self.ongoing_groups.remove_group(group_chat_id)

        self.bot.send_message(group_chat_id, "Angel & Mortal game ended!! Hope everyone had fun :) Press /startpoll to start a new round!")

    
