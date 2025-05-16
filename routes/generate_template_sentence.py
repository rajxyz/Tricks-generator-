import random

def generate_template_sentence(wordbank, templates, letters=None):
    if not templates:
        return "No templates available."

    sentence_template = random.choice(templates)

    return sentence_template.format(
        Article=random.choice(wordbank.get("articles", ["the"])),
        Adjective=random.choice(wordbank.get("adjectives", ["nice"])),
        Noun=random.choice(wordbank.get("nouns", ["thing"])),
        Verb=random.choice(wordbank.get("verbs", ["run"])),
        Adverb=random.choice(wordbank.get("adverbs", ["quickly"])),
        Preposition=random.choice(wordbank.get("prepositions", ["in"]))
    )
