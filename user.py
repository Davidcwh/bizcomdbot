# Encapsulates data of a telegram user
class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = '@' + username
        self.angel : User = None
        self.mortal : User = None

    def resetAngelMortal(self):
        self.angel = None
        self.mortal = None

    