
import json
import sys
import os
import time

# Import your LLM function
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/app/rag')))
from narators_hadith import extract_narrators_chain_with_llm

# File paths
INPUT_FILE = os.path.join(os.path.dirname(__file__), '../Results/Muwatta Malik', 'book_6.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '../Results/Muwatta_Malik_Modified', 'book_6.json')

def main():
    # Load the single book dictionary
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        book = json.load(f)

    hadiths = book.get('hadiths', [])

    for idx, hadith in enumerate(hadiths):
        english_text = hadith.get('english', '')
        if english_text:
            narrators, content = extract_narrators_chain_with_llm(english_text)
            hadith['narrators'] = narrators
            hadith['content'] = content
            print(f"✅ Processed hadith {idx+1}/{len(hadiths)} — sleeping 13 seconds...")
            time.sleep(13)
        else:
            print(f"⚠️ Skipping hadith {idx+1} — no English text found.")

    # Ensure output folder exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Save the updated book to the new location
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(book, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Done! Annotated file saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
