from user import User
from user_storage import UserStorage
from typing import List

# Encapsulates data and behaviour of a group of telegram users
class Group:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.users = UserStorage()

    def add_user(self, user : User):
        self.users.add_user(user)

    def get_users_list(self) -> List[User]:
        return self.users.get_users_list()
    
    def contains_user(self, user_id) -> bool:
        return self.users.contains_user(user_id)
    
    def remove_user(self, user_id):
        self.users.remove_user(user_id)
    