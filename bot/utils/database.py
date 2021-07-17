import pandas as pd
import numpy as np
import os
import sys
import logging


from ui.constants import FLUSH_AFTER


if sys.version_info >= (3, 9):
    logging.basicConfig(
        filename='data/bot.log',
        format='%(name)s %(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        encoding='utf-8',
        level=logging.DEBUG)
else:
    logging.basicConfig(
        filename='data/bot.log',
        format='%(name)s %(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)
logger = logging.getLogger("bot.database")


class Database:
    def __init__(self, filename) -> None:
        logger.debug(f"Request to create a DB assigned to {filename}")

        self.count = FLUSH_AFTER
        self.filename = filename
        self.columns = [
            'chat_id',
            'prompt',
            'reply',
            'character'
        ]

        if os.path.exists(self.filename):
            self.df = pd.read_csv(self.filename, index_col=0)
            logger.debug(f"Initialized DB from {filename}")
        else:
            self.df = pd.DataFrame(columns=self.columns).set_index('chat_id')
            logger.debug("Initialized DB from scratch")

    def update(self, chat_id, data):

        logger.debug(f"Update DB for {chat_id} with {data}")

        if chat_id not in self.df.index:
            self.df.loc[chat_id] = [np.nan, np.nan, np.nan]
        for column_name, value in data.items():
            self.df[column_name][chat_id] = value
            print(column_name, value)
        self.count -= 1

        if self.count == 0:
            self.flush()

    def initialize(self, chat_id):
        logger.debug(f"Clean DB data for {chat_id}")
        self.df.loc[chat_id] = [np.nan, np.nan, np.nan]
        self.count -= 1

        if self.count == 0:
            self.flush()

    def get(self, chat_id):
        logger.debug(f"Get DB data for {chat_id}")
        if chat_id in self.df.index:
            return self.df.loc[chat_id]
        else:
            return None

    def print(self):
        print(f"File: {self.filename}\n")
        print(self.df)

    def flush(self):
        self.df.to_csv(self.filename, encoding='utf-8')
        self.count = FLUSH_AFTER
        logger.debug("DB flushed")
