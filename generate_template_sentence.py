import random

def generate_template_sentence(wordbank, templates, letters=None):
    if not templates:
        return "No templates available."

    sentence_template = random.choice(templates)

    return sentence_template.format(
        Article=random.choice(wordbank.get("Articles", [""])),
        Adjective=random.choice(wordbank.get("adjectives", [""])),
        Noun=random.choice(wordbank.get("nouns", [""])),
        Verb=random.choice(wordbank.get("verbs", [""])),
        Adverb=random.choice(wordbank.get("adverbs", [""])),
        Preposition=random.choice(wordbank.get("prepositions", [""]))
    )
