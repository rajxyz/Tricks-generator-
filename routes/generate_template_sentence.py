# generate_templates_sentence.py

import json
import random

def load_templates(path):
    with open(path, 'r') as f:
        return json.load(f)["TEMPLATES"]

def generate_sentence(word_dict, templates):
    template = random.choice(templates)
    return template.format(
        Article=random.choice(word_dict["articles"]),
        Adjective=random.choice(word_dict["adjectives"]),
        Noun=random.choice(word_dict["nouns"]),
        Verb=random.choice(word_dict["verbs"]),
        Adverb=random.choice(word_dict["adverbs"]),
        Preposition=random.choice(word_dict["prepositions"]),
    )
