import random

def generate_template_sentence(wordbank, templates, letters=None):
    # templates should be a dict with a "TEMPLATES" key
    if not templates or "TEMPLATES" not in templates:
        return "No templates available."

    # Choose a random sentence template
    sentence_template = random.choice(templates["TEMPLATES"])

    # Fill in placeholders using the wordbank
    filled_sentence = sentence_template.format(
        Article=random.choice(wordbank.get("articles", ["the"])),
        Adjective=random.choice(wordbank.get("adjectives", ["nice"])),
        Noun=random.choice(wordbank.get("nouns", ["thing"])),
        Verb=random.choice(wordbank.get("verbs", ["run"])),
        Adverb=random.choice(wordbank.get("adverbs", ["quickly"])),
        Preposition=random.choice(wordbank.get("prepositions", ["in"]))
    )

    return filled_sentence
