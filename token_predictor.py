#token_predictor.py
from tokenizer import Tokenizer

class TokenPredictor:
    def __init__(self):
        self.tokenizer = Tokenizer()

    def predict_tokens(self, text):
        tokens = self.tokenizer.tokenize(text)
        return len(tokens)
