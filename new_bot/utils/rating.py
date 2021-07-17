import pandas as pd
import os
from datetime import datetime
import sys
import logging

from ui.constants import FLUSH_AFTER, reaction


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
logger = logging.getLogger("bot.rating")


class Rating:
    def __init__(self, filename) -> None:
        logger.debug(f"Request to create a RateLog assigned to {filename}")

        self.count = FLUSH_AFTER
        self.filename = filename
        self.columns = [
            'datetime',
            'chat_id',
            'prompt',
            'reply',
            'character',
            'rating'
        ]

        if os.path.exists(self.filename):
            self.df = pd.read_csv(self.filename)
            try:
                self.next = self.df.tail(1).index.item() + 1
            except Exception as e:
                self.next = 0
            logger.debug(f"Initialized RateLog from {filename}")
        else:
            self.df = pd.DataFrame(columns=self.columns)
            self.next = 0
            logger.debug("Initialized RateLog from scratch")

    def append(self, chat_id, prompt, 
               reply, character, rating):
        
        logger.debug(f"Update RateLog for {chat_id}")

        date_time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        binarized_rating = reaction.index(rating)

        self.df.loc[self.next] = [
            date_time,
            chat_id,
            prompt,
            reply,
            character,
            binarized_rating
        ]
        self.next += 1
        self.count -= 1

        if self.count == 0:
            self.flush()

    def print(self):
        print(f"File: {self.filename}\n")
        print(self.df)

    def flush(self):
        self.df.to_csv(self.filename, index=False, encoding='utf-8')
        self.count = FLUSH_AFTER
        logger.debug("RateLog flushed")
