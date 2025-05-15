import random

def generate_template_sentence(wordbank, templates, letters):
    categories = ["noun", "adjective", "verb", "adverb"]
    word_map = {}

    for i, letter in enumerate(letters):
        category = categories[i % len(categories)]
        words = wordbank.get(category + "s", {}).get(letter.upper(), [])
        if words:
            word_map[category] = random.choice(words)
        else:
            word_map[category] = letter  # fallback to letter if word not found

    count = len(letters)
    template_list = templates.get(str(count), [])

    if not template_list:
        return "No template available for this word count."

    template = random.choice(template_list)

    # Replace placeholders in template
    for key in ["noun", "verb", "adjective", "adverb"]:
        template = template.replace(f"{{{key}}}", word_map.get(key, ""))

    return template.capitalize()
