import os
import pandas as pd
import logging

from config.constants import UPDATES_BEFORE_FLUSH, reaction
from datetime import datetime


logging.basicConfig(
    filename='bot/data/bot.log',
    format='%(name)s %(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    encoding='utf-8',
    level=logging.DEBUG)
logger = logging.getLogger("bot.rating")


class Rating:
    def __init__(self, filename):
        self.filename = filename
        self.count = UPDATES_BEFORE_FLUSH
        if os.path.exists(filename):
            logger.info(f"Read rating storage from {filename}")
            self.data = pd.read_csv(filename, index_col=0)
            self.next_idx = self.data.tail(1).index.item() + 1
        else:
            logger.info("Created empty rating storage")
            self.data = pd.DataFrame(
                columns=[
                    'datetime',
                    'chat_id',
                    'prompt',
                    'reply',
                    'character',
                    'rating'
                ]
            )
            self.next_idx = 0

    def update(self, chat_id, prompt, reply, character, rating):

        date_time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        new_data = [
            date_time,
            chat_id,
            prompt,
            reply,
            character,
            reaction.index(rating)
        ]
        self.data.loc[self.next_idx] = new_data
        logger.debug(f"Adding {new_data} row to rating data")

        self.count -= 1
        if self.count == 0:
            self.flush()
            self.count = UPDATES_BEFORE_FLUSH

    def show(self):
        print(self.data)

    def flush(self):
        logger.debug(f"Flushing the rating to {self.filename}")
        self.data.to_csv(self.filename, index=False, encoding='utf-8')
        logger.debug("Flush complete")
