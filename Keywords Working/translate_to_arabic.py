import json
import requests
import time
from typing import List

def translate_to_arabic(text: str) -> str:
    """
    Translate English text to Arabic using Google Translate API
    """
    
    try:
        # Using Google Translate API (free tier)
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'en',  # source language: English
            'tl': 'ar',  # target language: Arabic
            'dt': 't',   # return translation
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

def translate_keywords_to_arabic():
    """
    Read English keywords and translate them to Arabic
    """
    # Read the English keywords file
    print("Reading English keywords...")
    with open('collected_meanings.json', 'r', encoding='utf-8') as file:
        english_keywords = json.load(file)
    
    arabic_keywords = []
    total_keywords = len(english_keywords)
    
    print(f"Starting translation of {total_keywords} keywords to Arabic...")
    print("This may take a few minutes due to API rate limits...")
    
    for i, keyword in enumerate(english_keywords, 1):
        print(f"Translating {i}/{total_keywords}: '{keyword}'")
        
        # Translate the keyword
        arabic_translation = translate_to_arabic(keyword)
        arabic_keywords.append(arabic_translation)
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(0.5)  # Wait 0.5 seconds between requests
        
        # Progress update every 50 translations
        if i % 50 == 0:
            print(f"Progress: {i}/{total_keywords} completed ({i/total_keywords*100:.1f}%)")
        
        # Save progress every 100 translations to avoid losing work
        if i % 100 == 0:
            print("Saving progress...")
            with open('collected_meanings_arabic_temp.json', 'w', encoding='utf-8') as file:
                json.dump(arabic_keywords, file, indent=2, ensure_ascii=False)
    
    # Save the final Arabic translations
    print("Saving Arabic translations...")
    with open('collected_meanings_arabic.json', 'w', encoding='utf-8') as file:
        json.dump(arabic_keywords, file, indent=2, ensure_ascii=False)
    
    # Remove temporary file if it exists
    try:
        import os
        if os.path.exists('collected_meanings_arabic_temp.json'):
            os.remove('collected_meanings_arabic_temp.json')
    except:
        pass
    
    print(f"Translation completed!")
    print(f"English file: collected_meanings.json ({len(english_keywords)} entries)")
    print(f"Arabic file: collected_meanings_arabic.json ({len(arabic_keywords)} entries)")
    print("Both files have the same indexing structure.")

if __name__ == "__main__":
    translate_keywords_to_arabic()
