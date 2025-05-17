from typing import List
import random
import re

def generate_template_sentence(template: str, wordbank: dict, input_letters: List[str]) -> str:
    """
    Generate a sentence by filling in the placeholders in the template
    using the given wordbank and input letters.

    Args:
        template (str): The template string with placeholders like {noun}, {verb}, etc.
        wordbank (dict): A dictionary where keys are parts of speech (e.g., 'noun') 
                         and values are lists of words.
        input_letters (List[str]): A list of letters that the chosen words must start with.

    Returns:
        str: The sentence with placeholders filled in.
    """

    def get_word(pos_tag: str, letter: str) -> str:
        words = wordbank.get(pos_tag, [])
        if not words:
            return f"[no_{pos_tag}]"
        filtered = [w for w in words if w.lower().startswith(letter.lower())]
        return random.choice(filtered) if filtered else f"[no_{pos_tag}_with_{letter}]"

    used_letters = set()

    def replacer(match):
        pos_tag = match.group(1)
        available_letters = [l for l in input_letters if l not in used_letters]
        letter = available_letters[0] if available_letters else random.choice(input_letters)
        used_letters.add(letter)
        return get_word(pos_tag, letter)

    sentence = re.sub(r"\{(\w+)\}", replacer, template)
    return sentence
