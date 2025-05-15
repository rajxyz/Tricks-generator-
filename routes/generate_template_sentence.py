import random

def generate_template_sentence(word_dict, templates, letters):
    if not templates:
        return "No templates available."

    template = random.choice(templates)

    return template.format(
        Article=random.choice(word_dict["articles"]),
        Adjective=random.choice(word_dict["adjectives"]),
        Noun=random.choice(word_dict["nouns"]),
        Verb=random.choice(word_dict["verbs"]),
        Adverb=random.choice(word_dict["adverbs"]),
        Preposition=random.choice(word_dict["prepositions"]),
    )
