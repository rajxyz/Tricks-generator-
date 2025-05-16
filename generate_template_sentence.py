import random

def generate_template_sentence(wordbank, templates, letters=None):
    if not templates:
        return "No templates available."

    # Fill all templates with random words first
    filled_templates = []
    for t in templates:
        sentence = t.format(
            article=random.choice(wordbank.get("articles", [""])),
            adjective=random.choice(wordbank.get("adjectives", [""])),
            noun=random.choice(wordbank.get("nouns", [""])),
            verb=random.choice(wordbank.get("verbs", [""])),
            adverb=random.choice(wordbank.get("adverbs", [""])),
            preposition=random.choice(wordbank.get("prepositions", [""]))
        )
        filled_templates.append(sentence)

    # Now filter on letters
    if letters:
        letters = [l.lower() for l in letters]
        filtered = [
            s for s in filled_templates if any(l in s.lower() for l in letters)
        ]
        if filtered:
            return random.choice(filtered)
        else:
            return random.choice(filled_templates)  # fallback
    else:
        return random.choice(filled_templates)
