import json
import requests
import time
from typing import List

def translate_to_urdu(text: str) -> str:
    """
    Translate English text to Urdu using Google Translate API
    """
    try:
        # Using Google Translate API (free tier)
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'en', 
            'tl': 'ur', 
            'dt': 't',   
            'q': text
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            translated_text = result[0][0][0]
            return translated_text
        else:
            print(f"Error translating '{text}': {response.status_code}")
            return text  # Return original if translation fails
            
    except Exception as e:
        print(f"Error translating '{text}': {str(e)}")
        return text  # Return original if translation fails

def translate_keywords_to_urdu():
    """
    Read English keywords and translate them to Urdu
    """
    # Read the English keywords file
    print("Reading English keywords...")
    with open('collected_meanings.json', 'r', encoding='utf-8') as file:
        english_keywords = json.load(file)
    
    urdu_keywords = []
    total_keywords = len(english_keywords)
    
    print(f"Starting translation of {total_keywords} keywords...")
    print("This may take a few minutes due to API rate limits...")
    
    for i, keyword in enumerate(english_keywords, 1):
        print(f"Translating {i}/{total_keywords}: '{keyword}'")
        
        # Translate the keyword
        urdu_translation = translate_to_urdu(keyword)
        urdu_keywords.append(urdu_translation)
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(0.5)  # Wait 0.5 seconds between requests
        
        # Progress update every 50 translations
        if i % 50 == 0:
            print(f"Progress: {i}/{total_keywords} completed ({i/total_keywords*100:.1f}%)")
    
    # Save the Urdu translations
    print("Saving Urdu translations...")
    with open('collected_meanings_urdu.json', 'w', encoding='utf-8') as file:
        json.dump(urdu_keywords, file, indent=2, ensure_ascii=False)
    
    print(f"Translation completed!")
    print(f"English file: collected_meanings.json ({len(english_keywords)} entries)")
    print(f"Urdu file: collected_meanings_urdu.json ({len(urdu_keywords)} entries)")
    print("Both files have the same indexing structure.")

if __name__ == "__main__":
    translate_keywords_to_urdu()
