def generate_fixed_lines_sentence(name: str, data: dict) -> str:
    print("\n--- DEBUGGING FIXED-LINE GENERATION ---")
    print(f"Input Name: {name}")
    
    if name in data:
        lines = data[name]
        print(f"Found lines: {lines}")
        sentence = "\n".join(lines)
        print(f"Final sentence:\n{sentence}")
        return sentence
    else:
        print(f"No data found for: {name}")
        return f"<No data for {name}>"
