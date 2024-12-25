class TokenBudgetManager:
    def __init__(self, token_budget):
        self.token_budget = token_budget
        self.tokens_used = 0

    def can_consume_tokens(self, tokens):
        return self.tokens_used + tokens <= self.token_budget

    def consume_tokens(self, tokens):
        if self.can_consume_tokens(tokens):
            self.tokens_used += tokens
            return True
        return False

    def reset(self):
        self.tokens_used = 0

    def get_remaining_tokens(self):
        return self.token_budget - self.tokens_used
