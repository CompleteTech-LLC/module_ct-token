# improved_code_base/core/token_optimizer.py

import re
import logging
from typing import Dict
import tiktoken

try:
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
except Exception as e:
    logging.error(f"Failed to initialize tiktoken encoding: {e}")
    encoding = tiktoken.get_encoding('cl100k_base')  # Fallback to base encoding


# Prepare the replacements dictionary with comprehensive substitutions
replacements = {
    # Technical terms
    'artificial intelligence': 'AI',
    'machine learning': 'ML',
    'natural language processing': 'NLP',
    # ... (additional replacements as needed)
    # Common phrases
    'do not': "don't",
    'can not': "can't",
    # ... (additional replacements as needed)
}

# Create a lowercased version of the replacements for case-insensitive matching
lower_replacements = {k.lower(): v for k, v in replacements.items()}

# Sort the replacements by decreasing length (so longer phrases are replaced first)
sorted_replacements = sorted(replacements.items(), key=lambda x: -len(x[0]))

# Extract keys for regex pattern
sorted_replacement_keys = [re.escape(k) for k, _ in sorted_replacements]

# Prepare regular expression pattern
pattern = re.compile(r'\b(' + '|'.join(sorted_replacement_keys) + r')\b', re.IGNORECASE)

# Precompute token counts for replacements
token_cache: Dict[str, int] = {}

# Precompile the sentence split pattern
sentence_split_pattern = re.compile(r'(?<=[.!?])\s+')


def encode_prompt(prompt: str) -> str:
    """
    Encode the prompt to minimize token usage while maintaining structure.
    This function applies token-aware replacements, including phrases.

    Args:
        prompt (str): The prompt to encode.

    Returns:
        str: The encoded prompt.
    """
    try:
        # Function to replace matches
        def replace_match(match):
            match_text = match.group(0)
            match_text_lower = match_text.lower()
            replacement = lower_replacements.get(match_text_lower)
            if replacement:
                # Check if replacement reduces token count
                if match_text_lower not in token_cache:
                    token_cache[match_text_lower] = len(encoding.encode(match_text))
                if replacement not in token_cache:
                    token_cache[replacement] = len(encoding.encode(replacement))
                original_token_count = token_cache[match_text_lower]
                replacement_token_count = token_cache[replacement]
                if replacement_token_count <= original_token_count:
                    return replacement
            return match_text  # Return original text if no replacement or not beneficial

        optimized_prompt = pattern.sub(replace_match, prompt)
        return optimized_prompt
    except Exception as e:
        logging.error(f"Error encoding prompt: {e}")
        return prompt


def optimize_prompt(prompt: str) -> str:
    """
    Optimize the given prompt for token usage while maintaining its full context and structure.

    Args:
        prompt (str): The original prompt.

    Returns:
        str: The optimized prompt.
    """
    try:
        # Remove unnecessary whitespace
        optimized = ' '.join(prompt.strip().split())

        # Remove duplicate sentences
        sentences = sentence_split_pattern.split(optimized)
        unique_sentences = []
        seen_sentences = set()
        for sentence in sentences:
            normalized_sentence = re.sub(r'\s+', ' ', sentence.strip().lower())
            if normalized_sentence not in seen_sentences:
                unique_sentences.append(sentence.strip())
                seen_sentences.add(normalized_sentence)

        optimized = ' '.join(unique_sentences)

        # Optimize the text by replacing phrases
        optimized = encode_prompt(optimized)

        # Truncate to token limit without cutting off in the middle of a sentence
        optimized = truncate_to_token_limit(optimized)
        return optimized
    except Exception as e:
        logging.error(f"Error optimizing prompt: {e}")
        return prompt


def truncate_to_token_limit(text: str, max_tokens: int = 2048) -> str:
    """
    Truncate the text to ensure it doesn't exceed the maximum token limit.
    Truncation is done at sentence boundaries to maintain full context.

    Args:
        text (str): The text to truncate.
        max_tokens (int): The maximum allowed tokens.

    Returns:
        str: The truncated text.
    """
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    # Find a suitable place to cut off
    sentences = sentence_split_pattern.split(text)
    truncated_text = ''
    total_tokens = 0
    for sentence in sentences:
        sentence = sentence.strip()
        sentence_tokens = encoding.encode(sentence + ' ')
        if total_tokens + len(sentence_tokens) <= max_tokens:
            truncated_text += sentence + ' '
            total_tokens += len(sentence_tokens)
        else:
            break
    return truncated_text.strip()


def get_token_count(text: str) -> int:
    """
    Get the exact number of tokens in the given text using tiktoken.

    Args:
        text (str): The text to analyze.

    Returns:
        int: The token count.
    """
    try:
        token_ids = encoding.encode(text)
        return len(token_ids)
    except Exception as e:
        logging.error(f"Error getting token count: {e}")
        return 0
