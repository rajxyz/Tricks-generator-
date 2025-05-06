import random

def generate_grammar_sentence(wordbank, letters):
    sentence = []

    categories = ["Nouns", "Verbs", "Adjectives", "Adverbs"]
    selected_words = {}

    for i, letter in enumerate(letters):
        category = categories[i % len(categories)]
        words = wordbank.get(category, {}).get(letter.upper(), [])
        if words:
            selected_words[category] = random.choice(words)
        else:
            selected_words[category] = letter

    # Simple SVO sentence with adjective and adverb
    noun = selected_words.get("Nouns", "")
    verb = selected_words.get("Verbs", "")
    adj = selected_words.get("Adjectives", "")
    adv = selected_words.get("Adverbs", "")

    sentence = f"The {adj} {noun} {verb}s {adv}."
    return sentence.capitalize()
