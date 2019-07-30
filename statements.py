from db import DB

class Statements:

    def __init__(self):
        self.db = DB('statements')

    def add(self, chat, message, user, text, parent):
        params = {'chat_id':str(chat), 'message_id':str(message), 'user_id':str(user), 'statement':'\''+text+'\''}
        if(parent != None):
            params['parent'] = str(parent)
        self.db.Write(params)

    def get(self, chat, message):
        return self.db.Read({'chat_id':str(chat), 'message_id':str(message)})
