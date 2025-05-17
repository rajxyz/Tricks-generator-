def generate_template_sentence(wordbank, templates, input_letters):
    if not input_letters or not templates:
        return "Invalid input."

    template = random.choice(templates)
    placeholders = re.findall(r"{(.*?)}", template)
    filled = {}

    for i, placeholder in enumerate(placeholders):
        letter = input_letters[i % len(input_letters)].upper()
        category = placeholder.capitalize() + "s"  # e.g., noun -> Nouns

        words_by_letter = wordbank.get(category, {})
        matching = words_by_letter.get(letter, [])

        if matching:
            filled[placeholder] = random.choice(matching)
        else:
            filled[placeholder] = f"[{placeholder}]"

    # Fill the template
    for key, val in filled.items():
        template = template.replace(f"{{{key}}}", val)

    return template
