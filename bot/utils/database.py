import os
import pandas as pd
import logging

from config.constants import UPDATES_BEFORE_FLUSH


logging.basicConfig(
    filename='bot/data/bot.log',
    format='%(name)s %(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    encoding='utf-8',
    level=logging.DEBUG)
logger = logging.getLogger("bot.db")


class Database:
    def __init__(self, filename):
        self.filename = filename
        self.count = UPDATES_BEFORE_FLUSH
        if os.path.exists(filename):
            logger.info(f"Read db from {filename}")
            self.data = pd.read_csv(filename, index_col=0)
        else:
            logger.info("Created empty db")
            self.data = pd.DataFrame(
                columns=[
                    'chat_id',
                    'character',
                    'prompt',
                    'reply',
                    'state'
                ]
            ).set_index('chat_id')

    def update(self, chat_id, character=None,
               prompt=None, reply=None, state=None):

        if chat_id in self.data.index:
            data = self.data.loc[chat_id]
            character = data["character"] if character is None else character
            prompt = data["prompt"] if prompt is None else prompt
            reply = data["reply"] if reply is None else reply
            state = data["state"] if state is None else state

        new_data = [character, prompt, reply, state]
        self.data.loc[chat_id] = new_data
        logger.debug(f"Updating {chat_id} state with {new_data}")

        self.count -= 1
        if self.count == 0:
            self.flush()
            self.count = UPDATES_BEFORE_FLUSH

    def get(self, chat_id):
        logger.debug(f"Getting {chat_id} row from db")
        if chat_id in self.data.index:
            return self.data.loc[chat_id]
        else:
            return None

    def show(self):
        print(self.data)

    def flush(self):
        logger.debug(f"Flushing the db to {self.filename}")
        self.data.to_csv(self.filename, encoding='utf-8')
        logger.debug("Flush complete")
