from user import User
from typing import List

# Encapsulates data and behaviour of a collection of users
class UserStorage:
    def __init__(self):
        self.users = dict() # format: { user id : user object }
    
    # return false if user to be added already exists, and true if user is added successfully
    def add_user(self, user : User) -> bool:
        if self.contains_user(user.user_id):
            return False
        
        self.users[user.user_id] = user
        return True

    def get_user(self, user_id) -> User:
        return self.users[user_id]
    
    def get_users_list(self) -> List[User]:
        users_list = []

        for user_id in self.users.keys():
            users_list.append(self.users[user_id])

        return users_list
    
    # return false if user to be removed does not exists, and true if user is removed successfully
    def remove_user(self, user_id) -> bool:
        if self.contains_user(user_id):
            self.users.pop(user_id)
            return True
        
        return False
    
    def contains_user(self, user_id) -> bool:
        return user_id in self.users.keys()