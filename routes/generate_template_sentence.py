import random

def generate_template_sentence(wordbank, templates, letters=None):
    if not templates:
        return "No templates available."

    if letters:
        letters = [l.lower() for l in letters]
        filtered = [
            t for t in templates if any(l in t.lower() for l in letters)
        ]
        if filtered:
            sentence_template = random.choice(filtered)
        else:
            sentence_template = random.choice(templates)  # fallback
    else:
        sentence_template = random.choice(templates)

    return sentence_template.format(
        article=random.choice(wordbank.get("articles", [""])),
        adjective=random.choice(wordbank.get("adjectives", [""])),
        noun=random.choice(wordbank.get("nouns", [""])),
        verb=random.choice(wordbank.get("verbs", [""])),
        adverb=random.choice(wordbank.get("adverbs", [""])),
        preposition=random.choice(wordbank.get("prepositions", [""]))
    )
