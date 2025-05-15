import random

def generate_template_sentence(wordbank, templates, letters):
    words = []
    for letter in letters:
        choices = wordbank.get(letter.upper())
        if choices:
            words.append(random.choice(choices))
        else:
            words.append(letter)

    count = len(words)

    # Filter templates where count matches
    filtered_templates = [tpl["template"] for tpl in templates if tpl.get("count") == count]

    if not filtered_templates:
        return f"No template found for {count} words: {' '.join(words)}"

    selected_template = random.choice(filtered_templates)
    sentence = selected_template

    for i, word in enumerate(words):
        sentence = sentence.replace(f"{{{i}}}", word)

    return sentence
