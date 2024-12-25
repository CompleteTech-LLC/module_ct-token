# token_usage_tracker.py

import tiktoken
import logging
from functools import lru_cache

class TokenUsageTracker:
    def __init__(self, max_cache_size=1000):
        self.total_tokens_used = 0
        try:
            self.encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        except Exception as e:
            logging.error(f"Failed to initialize tiktoken encoding: {e}")
            self.encoding = tiktoken.get_encoding('cl100k_base')
        self.max_cache_size = max_cache_size
        self._encode_and_count = lru_cache(maxsize=self.max_cache_size)(self._encode_and_count)

    def _encode_and_count(self, text):
        tokens = self.encoding.encode(text)
        return len(tokens)

    def count_tokens(self, text):
        num_tokens = self._encode_and_count(text)
        self.total_tokens_used += num_tokens
        return num_tokens

    def get_total_tokens_used(self):
        return self.total_tokens_used

    def reset(self):
        self.total_tokens_used = 0
        self._encode_and_count.cache_clear()
