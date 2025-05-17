def generate_template_sentence(template: str, grammar_helpers: dict, wordbank: dict, input_letters: List[str]) -> str:
    placeholders = re.findall(r'([a-z_]+)', template.lower())

    for ph in placeholders:
        replacement = None
        key = ph.lower()

        # 1. Grammar helpers
        if key in grammar_helpers and grammar_helpers[key]:
            replacement = random.choice(grammar_helpers[key])

        # 2. Flat list wordbank
        elif key in wordbank and isinstance(wordbank[key], list):
            replacement = random.choice(wordbank[key]) if wordbank[key] else None

        # 3. Letter-based wordbank: Nouns, Verbs, Adjectives, Adverbs
        elif key in ["noun", "verb", "adjective", "adverb"]:
            category = key.capitalize() + 's'  # e.g., Nouns
            if category in wordbank:
                word_list = []
                for letter in input_letters:
                    word_list.extend(wordbank[category].get(letter.upper(), []))
                if word_list:
                    replacement = random.choice(word_list)

        # Fallback
        if not replacement:
            replacement = f"<{ph}>"

        # Replace only one occurrence at a time
        template = re.sub(rf'{ph}', replacement, template, count=1)

    return template
