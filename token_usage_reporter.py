#token_usage_reporter.py
from tools import tools_manager

class TokenUsageReporter:
    def __init__(self, token_usage_tracker):
        self.token_usage_tracker = token_usage_tracker

    def generate_report(self):
        total_tokens_used = self.token_usage_tracker.get_total_tokens_used()
        report = f"Total tokens used during the session: {total_tokens_used}"
        tools_manager.execute("log_message", message=report)
        return report
