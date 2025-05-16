import random

def generate_template_sentence(wordbank, templates, letters=None):
    if not isinstance(templates, dict) or "TEMPLATES" not in templates:
        return "No templates available."

    try:
        sentence_template = random.choice(templates["TEMPLATES"])
        sentence = sentence_template.format(
            Article=random.choice(wordbank.get("articles", ["the"])),
            Adjective=random.choice(wordbank.get("adjectives", ["nice"])),
            Noun=random.choice(wordbank.get("nouns", ["thing"])),
            Verb=random.choice(wordbank.get("verbs", ["run"])),
            Adverb=random.choice(wordbank.get("adverbs", ["quickly"])),
            Preposition=random.choice(wordbank.get("prepositions", ["in"]))
        )
        return sentence
    except KeyError as e:
        return f"Template placeholder missing: {e}"
    except Exception as e:
        return f"Error generating sentence: {str(e)}"
