import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import logging
from utils.exceptions import ModelError


logging.basicConfig(
    filename='bot/data/bot.log',
    format='%(name)s %(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    encoding='utf-8',
    level=logging.DEBUG)
logger = logging.getLogger("bot.model")

np.random.seed(42)
torch.manual_seed(42)


class Model:
    def __init__(self, char_name, model_name):
        self.character = char_name
        if model_name != '':
            self.tok = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
        else:
            self.tok = self.model = None

    def get_reply(self, text) -> str:
        if self.tok is not None and self.model is not None:
            text = f"HEДРУГ: {text}\n{self.character}:"

            generated_text = ""
            inpt = self.tok.encode(text, return_tensors="pt")
            out = self.model.generate(
                inpt, max_length=50, repetition_penalty=5.0, 
                do_sample=True, top_k=5, top_p=0.95, temperature=1)

            try:
                generated_text = self.tok.decode(out[0])
                generated_text = generated_text[len(text):]
                tag = generated_text.find("</s>")
                if tag > -1:
                    generated_text = generated_text[:tag]
                else:
                    explanation = f"Tag </s> not found in generated for prompt {text}"
                    logger.error(explanation)
                    generated_text = generated_text
            except Exception as e:
                raise ModelError(f"Error {e} occured!")
            return generated_text
        else:
            return "Model or Tokenizer not working"


def load_models(names: dict) -> dict:
    mds = dict()
    for name, model_name in names.items():
        mds[name] = Model(name, model_name)

    return mds
