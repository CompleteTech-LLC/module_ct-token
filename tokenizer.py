import re

class Tokenizer:
    def __init__(self, vocabulary=None):
        self.vocabulary = vocabulary or {}
        self.inverse_vocabulary = {v: k for k, v in self.vocabulary.items()}

    def tokenize(self, text):
        tokens = []
        words = re.findall(r'\S+', text)
        for word in words:
            if word not in self.vocabulary:
                token_id = len(self.vocabulary) + 1
                self.vocabulary[word] = token_id
                self.inverse_vocabulary[token_id] = word
            else:
                token_id = self.vocabulary[word]
            tokens.append(token_id)
        return tokens

    def detokenize(self, tokens):
        words = [self.inverse_vocabulary.get(token_id, '') for token_id in tokens]
        return ' '.join(words)
