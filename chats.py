from telebot.apihelper import ApiTelegramException

class Chats:
    def __init__(self, bot):
        self.bot = bot

        # contains { angel user id : mortal user id } and 
        # { mortal user id : angel user id } respectively
        self.angel_to_mortal = dict()
        self.mortal_to_angel = dict()

        # contains { user id : chat id}
        self.user_chat_id = dict()

        # contains { group chat id : list of user id}
        self.group_to_users = dict()
    
    def add_pairings(self, pairing_info):
        group_chat_id = pairing_info["group_chat_id"]
        user_id_list = pairing_info["user_id_list"]

        if group_chat_id in self.group_to_users.keys():
            return
        
        self.group_to_users[group_chat_id] = user_id_list

        angel_to_mortal = pairing_info["angel_to_mortal"]
        user_chat_id = pairing_info["user_chat_id"]

        for angel_id in angel_to_mortal.keys():
            mortal_id = angel_to_mortal[angel_id]

            if angel_id not in self.angel_to_mortal.keys():
                self.angel_to_mortal[angel_id] = mortal_id
            
            if mortal_id not in self.mortal_to_angel.keys():
                self.mortal_to_angel[mortal_id] = angel_id

            if angel_id not in self.user_chat_id.keys():
                self.user_chat_id[angel_id] = user_chat_id[angel_id]

    def send_message_to_angel(self, message, mortal_id):
        if message == "":
            return

        angel_id = self.mortal_to_angel[mortal_id]
        angel_chat_id = self.user_chat_id[angel_id]
        message = "Your mortal: " + message

        try:
            self.bot.send_message(angel_chat_id, message)
        except ApiTelegramException as e:
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user': 
                mortal_chat_id = self.user_chat_id[mortal_id]
                self.bot.send_message(mortal_chat_id, "Oops looks like your angel deleted the chat with the bot, can't send them messages :/")


    def send_message_to_mortal(self, message, angel_id):
        if message == "":
            return
        
        mortal_id = self.angel_to_mortal[angel_id]
        mortal_chat_id = self.user_chat_id[mortal_id]
        message = "Your angel: " + message

        try:
            self.bot.send_message(mortal_chat_id, message)
        except ApiTelegramException as e:
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user': 
                angel_chat_id = self.user_chat_id[angel_id]
                self.bot.send_message(angel_chat_id, "Oops looks like your mortal deleted the chat with the bot, can't send them messages :/")

    def stop_game(self, group_chat_id):
        if group_chat_id not in self.group_to_users.keys():
            self.bot.send_message(group_chat_id, "There's no existing Angel & Mortal game for this group chat!")
            return
        
        user_id_list = self.group_to_users[group_chat_id]
        for user_id in user_id_list:
            if user_id in self.angel_to_mortal.keys():
                self.angel_to_mortal.pop(user_id)

            if user_id in self.mortal_to_angel.keys():
                self.mortal_to_angel.pop(user_id)

            if user_id in self.user_chat_id.keys():
                self.user_chat_id.pop(user_id)
        
        self.group_to_users.pop(group_chat_id)

        self.bot.send_message(group_chat_id, "Angel & Mortal game ended!! Hope everyone had fun :) Press /startpoll to start a new round!")

    
