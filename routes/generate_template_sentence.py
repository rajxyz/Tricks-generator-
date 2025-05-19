import random
import inflect

p = inflect.engine()

def generate_template_sentence(template: str, wordbank: dict, input_letters: list) -> str:
    print("\n--- DEBUGGING TEMPLATE GENERATION ---")
    print(f"Original template: {template}")
    print(f"Input letters: {input_letters}")

    # Detect placeholders manually by scanning the template for '[...]'
    placeholders = []
    start = 0
    while True:
        start = template.find('[', start)
        if start == -1:
            break
        end = template.find(']', start)
        if end == -1:
            break
        ph = template[start+1:end]
        placeholders.append(ph)
        start = end + 1

    print(f"Detected placeholders: {placeholders}")

    for ph in placeholders:
        plural = False
        base_ph = ph

        # Check if plural (ends with s and base is valid placeholder)
        if base_ph.endswith('s') and base_ph[:-1] in ['noun', 'verb', 'adjective', 'adverb']:
            plural = True
            base_ph = base_ph[:-1]

        # Capitalize key as in your wordbank JSON keys
        json_key = base_ph.capitalize() + 's' if base_ph in ['noun', 'verb', 'adjective', 'adverb'] else base_ph

        print(f"\nHandling placeholder: {ph}")
        print(f"Base placeholder: {base_ph}")
        print(f"Plural: {plural}")
        print(f"Looking in wordbank key: {json_key}")

        word_list = []
        for letter in input_letters:
            upper_letter = letter.upper()
            matched = wordbank.get(json_key, {}).get(upper_letter, [])
            print(f"  Letter '{upper_letter}' => {matched}")
            word_list.extend(matched)

        if word_list:
            word = random.choice(word_list)
            if plural:
                word = p.plural(word)
            print(f"Chosen word: {word}")
        else:
            word = f"<{ph}>"
            print(f"No match found, using placeholder: {word}")

        # Replace only the first occurrence of this placeholder in template
        template = template.replace(f"[{ph}]", word, 1)

    print(f"Final sentence: {template}")
    return template
