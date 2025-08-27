import json

# Load both files
with open('collected_meanings.json', 'r', encoding='utf-8') as f:
    english_keywords = json.load(f)

with open('collected_meanings_urdu.json', 'r', encoding='utf-8') as f:
    urdu_keywords = json.load(f)

print("Index verification (English -> Urdu):")
print("-" * 60)

# Check first 10 entries to verify indexing
for i in range(10):
    print(f"Index {i:2d}: '{english_keywords[i]}' -> '{urdu_keywords[i]}'")

print("-" * 60)
print(f"Total English entries: {len(english_keywords)}")
print(f"Total Urdu entries: {len(urdu_keywords)}")
print(f"Indexing matches: {len(english_keywords) == len(urdu_keywords)}")

# Check some specific examples
print("\nSample translations:")
sample_indices = [32, 33, 37, 40, 41]  # Names and common words
for i in sample_indices:
    print(f"'{english_keywords[i]}' -> '{urdu_keywords[i]}'")
