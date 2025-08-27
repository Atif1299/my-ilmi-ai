import json
import os

# Paths
TRANSLATION_FILE = "quran.json"
BEFORE_FOLDER = "before"
AFTER_FOLDER = "after"

# Load translation JSON
with open(TRANSLATION_FILE, "r", encoding="utf-8") as f:
    translations_data = json.load(f)

# Build lookup dictionary
# Key: (juz, surah_number, aya_number)
translation_lookup = {
    (t["juz"], t["surah_number"], t["aya_number"]): t["english_translation"]
    for t in translations_data
}

# Ensure output folder exists
os.makedirs(AFTER_FOLDER, exist_ok=True)

# Process all files in BEFORE_FOLDER
for filename in os.listdir(BEFORE_FOLDER):
    if filename.endswith(".json"):
        input_path = os.path.join(BEFORE_FOLDER, filename)
        output_path = os.path.join(AFTER_FOLDER, filename)

        with open(input_path, "r", encoding="utf-8") as f:
            words_data = json.load(f)

        for entry in words_data:
            for occ in entry.get("occurrences", []):
                surah = occ["verse_reference"]["surah"]
                verse = occ["verse_reference"]["verse"]

                # Try to find translation (loop because juz not in occ)
                matched = None
                for (juz, s, v), translation in translation_lookup.items():
                    if s == surah and v == verse:
                        matched = translation
                        break

                if matched:
                    occ["english_translation"] = matched
                else:
                    occ["english_translation"] = None
                    print(f"❌ Missing translation in {filename} → Surah {surah}, Ayah {verse}")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(words_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Processed: {filename}")

print("🔎 Done. Check 'after/' folder and console for errors.")
