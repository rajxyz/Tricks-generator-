import random

def generate_grammar_sentence_hinglish(wordbank, letters):
    sentence = []

    categories = ["Nouns", "Verbs", "Adjectives", "Adverbs"]
    selected_words = {}

    for i, letter in enumerate(letters):
        category = categories[i % len(categories)]
        words_by_letter = wordbank.get(category, {})
        words = words_by_letter.get(letter.upper(), [])
        if words:
            selected_words[category] = random.choice(words)
        else:
            selected_words[category] = ""  # Better fallback

    noun = selected_words.get("Nouns", "").strip()
    verb = selected_words.get("Verbs", "").strip()
    adj = selected_words.get("Adjectives", "").strip()
    adv = selected_words.get("Adverbs", "").strip()

    # Build sentence parts safely
    parts = ["Woh"]
    if adj:
        parts.append(adj)
    if noun:
        parts.append(noun)
    if verb:
        parts.append(verb)
    if adv:
        parts.append(adv)

    return " ".join(parts).capitalize() + "."
