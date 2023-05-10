from group import Group

# Encapsulates the data and behaviour of a collection of groups
class GroupStorage:
    def __init__(self):
        self.groups = dict() # format: { chat_id : group object }
    
    def add_group(self, group : Group) -> bool:
        if self.contains_group(group.chat_id):
            return False
        
        self.groups[group.chat_id] = group
        return True
    
    def get_group(self, chat_id) -> Group:
        return self.groups[chat_id]
    
    def remove_group(self, chat_id) -> bool:
        if self.contains_group(chat_id):
            self.groups.pop(chat_id)
            return True
        
        return False
    
    def contains_group(self, chat_id) -> bool:
        return chat_id in self.groups.keys()