from cachetools import TTLCache
from utils.token_counter import token_counter

class MemoryChatRepository:
              
    def __init__(self):
        
        # Max. 300 users, each entry lasts 30 minutes
        self.user_histories = TTLCache(maxsize=300, ttl=1800)
    
    # Function to retrieve a user's history
    def get_memory(self,chat_id: str):
        if chat_id not in self.user_histories:
            # Create an initial memory for new chats
            self.user_histories[chat_id] = [{"role": "system", "content": "You are an expert in data analysis and respond to user queries in Markdown format."}]
        return self.user_histories[chat_id]

    # Function to trim history if it is too long
    def trim_history(self,history, max_tokens: int,model:str):
        all_content = " ".join(item["content"] for item in history)
        tokens_used,_= token_counter(all_content,model)
        while tokens_used > max_tokens:
            history.pop(1)  # Delete the second message (after the system message)
            tokens_used = sum(len(item["content"]) for item in history)
        return history

    # Function to update a user's history
    def update_memory(self,chat_id: str, role: str, content: str, max_token_output: int,model:str):
        history = self.get_memory(chat_id)
        history.append({"role": role, "content": content})
        # Limitar el historial para evitar exceder el límite de tokens
        self.user_histories[chat_id] = self.trim_history(history, max_token_output,model)
        return ""