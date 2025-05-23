import random
import re

def get_actors_by_letter(letter, wordbank):
    print(f"--- DEBUG ACTORS ---")
    print(f"Input letter(s): {letter}")
    letters = [l.strip().upper() for l in letter.split(',')]
    print(f"Parsed letters: {letters}")

    result = []
    for l in letters:
        names = wordbank.get("Actors", {}).get(l, [])
        print(f"Letter '{l}' => {names}")
        result += names

    return result


def get_mnemonics_by_letter(letter, wordbank):
    print(f"--- DEBUG MNEMONICS ---")
    print(f"Input letter(s): {letter}")
    letters = [l.strip().upper() for l in letter.split(',')]
    print(f"Parsed letters: {letters}")

    result = []
    for l in letters:
        tricks = wordbank.get("Mnemonics", {}).get(l, [])
        print(f"Letter '{l}' => {tricks}")
        result += tricks

    return result


def get_questions_by_letter(letter, wordbank):
    print(f"--- DEBUG QUESTIONS ---")
    print(f"Input letter(s): {letter}")
    letters = [l.strip().upper() for l in letter.split(',')]
    print(f"Parsed letters: {letters}")

    result = []
    for l in letters:
        questions = wordbank.get("Questions", {}).get(l, [])
        print(f"Letter '{l}' => {questions}")
        result += questions

    return result


def generate_sentence(template, letters, wordbank):
    print("--- DEBUGGING TEMPLATE GENERATION ---")
    print(f"Original template: {template}")
    print(f"Input letters: {letters}")

    placeholders = re.findall(r"\{(.*?)\}", template)
    print(f"Detected placeholders: {placeholders}")

    used_words = {}

    for placeholder in placeholders:
        base_placeholder = placeholder.lower()
        print(f"Handling placeholder: {placeholder}")
        plural = placeholder.endswith("s")
        print(f"Base placeholder: {base_placeholder}")
        print(f"Plural: {plural}")

        key = None
        if base_placeholder.startswith("noun"):
            key = "Nouns"
        elif base_placeholder.startswith("verb"):
            key = "Verbs"
        elif base_placeholder.startswith("adjective"):
            key = "Adjectives"
        elif base_placeholder.startswith("article"):
            key = "article"
        elif base_placeholder.startswith("preposition"):
            key = "preposition"

        print(f"Looking in wordbank key: {key}")
        if not key:
            used_words[placeholder] = f"<{placeholder}>"
            continue

        words = []
        for l in letters:
            matches = wordbank.get(key, {}).get(l.upper(), [])
            print(f"  Letter '{l.upper()}' => {matches}")
            words += matches

        if not words:
            used_words[placeholder] = f"<{placeholder}>"
        else:
            chosen_word = random.choice(words)
            used_words[placeholder] = chosen_word if not plural else chosen_word + "s"
            print(f"Chosen word: {used_words[placeholder]}")

    final_sentence = template
    for key, val in used_words.items():
        final_sentence = final_sentence.replace(f"{{{key}}}", val)

    print(f"Final sentence: {final_sentence}")
    return final_sentence
