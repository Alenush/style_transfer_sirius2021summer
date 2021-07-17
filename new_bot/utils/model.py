import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import logging
from tqdm import tqdm
import sys

from ui.exceptions import ModelError


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
logger = logging.getLogger("bot.model")

np.random.seed(42)
torch.manual_seed(42)


class Model:
    def __init__(self, character, model_name):
        logger.debug(f"Model for {character} loading from {model_name}")

        self.character = character
        self.with_gpu = torch.cuda.is_available()

        # If model is not loaded for test purposes
        if model_name != '':
            self.tok = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name)

            if self.with_gpu:
                self.model.cuda()

            logger.debug(f"Model for {character} loaded from {model_name}")
        else:
            self.tok = self.model = None
            logger.error(f"Model for {character} not loaded from {model_name}")

    def get_reply(self, text) -> str:
        if (self.tok is not None) and (self.model is not None):
            logger.debug(f"Model generates reply for {text}")

            generated_text = "Generation error"
            text = f"HEДРУГ: {text}\n{self.character}:"
            inpt = self.tok.encode(text, return_tensors="pt")

            if self.with_gpu:
                out = self.model.generate(
                    inpt.cuda(),
                    max_length=50,
                    repetition_penalty=5.0,
                    do_sample=True,
                    top_k=5,
                    top_p=0.95,
                    temperature=1
                )
            else:
                out = self.model.generate(
                    inpt,
                    max_length=50,
                    repetition_penalty=5.0,
                    do_sample=True,
                    top_k=5,
                    top_p=0.95,
                    temperature=1
                )

            try:
                generated_text = self.tok.decode(out[0])
                generated_text = generated_text[len(text):]
                tag_idx = generated_text.find("</s>")
                if tag_idx > -1:
                    generated_text = generated_text[:tag_idx]

                    log_msg = "Model generates reply {} for {}".format(
                        generated_text,
                        text
                    )
                    logger.debug(log_msg)
                else:
                    logger.error(
                        "Tag </s> not found in generated for prompt " +
                        text
                    )
            except Exception as e:
                logger.error(f"Raised an {e} exception!")
                raise ModelError(f"Error {e} occured!")
            return f"{self.character}: {generated_text}"
        else:
            logger.error(f"Model for character {self.character} not loaded.")
            return f"Model for character {self.character} not loaded."


def load_models(names: dict) -> dict:
    print("Loading models:")
    logger.debug(f"Loading models: from {names}")

    mds = dict()
    for name, model_name in tqdm(names.items()):
        mds[name] = Model(name, model_name)

    return mds
