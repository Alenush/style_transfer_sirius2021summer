import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from utils.exceptions import ModelError


np.random.seed(42)
torch.manual_seed(42)


class Model:
    def __init__(self, model_name) -> None:
        self.tok = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.cuda()

    def get_reply(self, text) -> str:
        text = f"HEДРУГ: {text}\nФИБИ:"

        generated_text = ""
        inpt = self.tok.encode(
            text, add_special_tokens=False, return_tensors="pt")
        output_sequences = self.model.generate(
            inpt.cuda(), max_length=50, repetition_penalty=5.0,
            do_sample=True, top_k=5, top_p=0.95)

        if len(output_sequences):
            output_sequences = output_sequences[0]
            generated_text = self.tok.decode(output_sequences)
            tag = generated_text.find("</s>")
            if tag > -1:
                generated_text = generated_text[:tag]
            else:
                raise ModelError("Some error occured!")
        return generated_text


def load_models(names: dict) -> dict:
    mds = dict()
    for name, model_name in names.items():
        mds[name] = Model(model_name)

    return mds
