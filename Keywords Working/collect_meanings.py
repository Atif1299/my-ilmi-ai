import os
import json

# Folder containing the JSON files
folder_path = os.path.join(os.path.dirname(__file__), 'Quran Dictionary With English Translation')

meanings = []

for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Each file may contain a list of dicts or a single dict
                if isinstance(data, list):
                    for item in data:
                        meaning = item.get('meaning')
                        if meaning:
                            meanings.append(meaning)
                elif isinstance(data, dict):
                    meaning = data.get('meaning')
                    if meaning:
                        meanings.append(meaning)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# Write all collected meanings to a new file
output_path = os.path.join(os.path.dirname(__file__), 'collected_meanings_in_english.json')
with open(output_path, 'w', encoding='utf-8') as out_f:
    json.dump(meanings, out_f, ensure_ascii=False, indent=2)

print(f"Collected {len(meanings)} meanings. Output written to {output_path}")
