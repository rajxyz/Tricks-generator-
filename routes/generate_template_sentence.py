import random

def generate_template_sentence(wordbank, templates, letters=None):
    if not templates:
        return "No templates available."

    sentence_template = random.choice(templates)

    return sentence_template.format(
        Article=random.choice(wordbank["articles"]),
        Adjective=random.choice(wordbank["adjectives"]),
        Noun=random.choice(wordbank["nouns"]),
        Verb=random.choice(wordbank["verbs"]),
        Adverb=random.choice(wordbank["adverbs"]),
        Preposition=random.choice(wordbank["prepositions"])
    )
