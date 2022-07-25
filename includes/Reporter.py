import requests

class Reporter():

    def __init__(self, bot_token, chat_ids) -> None:
        self.bot_token = bot_token
        self.chat_ids = chat_ids

    def error(self, message):

        responses = []
        for chat_id in self.chat_ids: 
            responses.append(requests.post(f"https://api.telegram.org/bot{self.bot_token}/sendMessage", data={"chat_id": chat_id, "text":message}))
        return responses

