# token_optimizer.py

import re
import logging
from typing import List, Dict
import tiktoken

# Initialize tiktoken encoding
try:
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
except Exception as e:
    logging.error(f"Failed to initialize tiktoken encoding: {e}")
    encoding = tiktoken.get_encoding('cl100k_base')

# Define replacements: phrases to be replaced with shorter equivalents
replacements = {
    'artificial intelligence': 'AI',
    'machine learning': 'ML',
    'natural language processing': 'NLP',
    # ... (remaining replacements)
    'without': 'w/o'
}

# Create lowercase replacements for case-insensitive matching
lower_replacements = {phrase.lower(): replacement for phrase, replacement in replacements.items()}

# Precompute token counts for phrases and replacements
phrase_token_counts = {}
replacement_token_counts = {}

for phrase, replacement in lower_replacements.items():
    try:
        phrase_tokens = len(encoding.encode(phrase))
    except Exception as e:
        logging.error(f"Error encoding phrase '{phrase}': {e}")
        phrase_tokens = len(phrase.split())
    try:
        replacement_tokens = len(encoding.encode(replacement))
    except Exception as e:
        logging.error(f"Error encoding replacement '{replacement}': {e}")
        replacement_tokens = len(replacement.split())

    phrase_token_counts[phrase] = phrase_tokens
    replacement_token_counts[replacement] = replacement_tokens

# Filter out replacements that do not save tokens
effective_replacements = {}
for phrase, replacement in lower_replacements.items():
    phrase_tokens = phrase_token_counts[phrase]
    replacement_tokens = replacement_token_counts[replacement]
    if replacement_tokens < phrase_tokens:
        effective_replacements[phrase] = replacement

# Compile regular expression pattern for phrase matching using effective replacements
pattern = re.compile(r'\b(' + '|'.join(re.escape(phrase) for phrase in sorted(effective_replacements.keys(), key=len, reverse=True)) + r')\b', re.IGNORECASE)


def encode_prompt(prompt: str) -> str:
    """
    Replace phrases in the prompt with shorter equivalents if it reduces token count.
    """
    def replacement_func(match):
        original_phrase = match.group(0)
        lower_phrase = original_phrase.lower()
        replacement = effective_replacements.get(lower_phrase)
        if replacement:
            if original_phrase.isupper():
                return replacement.upper()
            elif original_phrase[0].isupper():
                return replacement.capitalize()
            else:
                return replacement
        return original_phrase

    optimized_prompt = pattern.sub(replacement_func, prompt)
    return optimized_prompt


def optimize_prompt(prompt: str) -> str:
    """
    Optimize the prompt by removing duplicate sentences and replacing phrases.
    """
    # Remove extra whitespace and split into sentences
    prompt = ' '.join(prompt.strip().split())
    sentences = re.split(r'(?<=[.!?])\s+', prompt)
    unique_sentences = []
    seen_sentences = set()
    for sentence in sentences:
        normalized_sentence = re.sub(r'\s+', ' ', sentence.strip().lower())
        if normalized_sentence not in seen_sentences:
            unique_sentences.append(sentence.strip())
            seen_sentences.add(normalized_sentence)
    # Reconstruct the prompt
    prompt = ' '.join(unique_sentences)
    # Replace phrases
    prompt = encode_prompt(prompt)
    # Truncate to token limit
    prompt = truncate_to_token_limit(prompt)
    return prompt


def truncate_to_token_limit(text: str, max_tokens: int = 2048) -> str:
    """
    Truncate the text to fit within the maximum token limit.
    """
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    truncated_text = ''
    token_count = 0
    for sentence in sentences:
        sentence_tokens = encoding.encode(sentence + ' ')
        if token_count + len(sentence_tokens) <= max_tokens:
            truncated_text += sentence + ' '
            token_count += len(sentence_tokens)
        else:
            break
    return truncated_text.strip()


def get_token_count(text: str) -> int:
    """
    Get the number of tokens in the text.
    """
    tokens = encoding.encode(text)
    return len(tokens)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        sample_prompt = sys.argv[1]
    else:
        sample_prompt = 'Your sample prompt text here.'
    optimized_prompt = optimize_prompt(sample_prompt)
    tokens_before = get_token_count(sample_prompt)
    tokens_after = get_token_count(optimized_prompt)
    print(f"Original Prompt ({tokens_before} tokens): {sample_prompt}")
    print(f"Optimized Prompt ({tokens_after} tokens): {optimized_prompt}")
    print(f"Tokens saved: {tokens_before - tokens_after}")