import json

input_path = "collected_meanings_in_english.json"
output_path = "collected_meanings_in_english_no_to.json"  # Change to input_path to overwrite

with open(input_path, "r", encoding="utf-8") as f:
    keywords = json.load(f)

cleaned_keywords = [
    kw[3:] if kw.lower().startswith("to ") else kw
    for kw in keywords
]

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_keywords, f, ensure_ascii=False, indent=2)

print(f"Cleaned keywords saved to {output_path}")