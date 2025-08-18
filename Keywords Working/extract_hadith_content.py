import json
import os
from pathlib import Path

def extract_all_hadith_content():
    """
    Extract all 'content' attributes from hadiths in all book JSON files
    and create a single JSON file containing all content.
    """
    
    # Path to the Muwatta_Malik_Modified folder
    books_folder = Path("../../hadith-data/Results/Books With Narators And Contents/Muwatta_Malik")
    
    # List to store all content
    all_content = []
    
    # Get all JSON files in the folder
    json_files = sorted([f for f in os.listdir(books_folder) if f.endswith('.json')])
    
    print(f"Found {len(json_files)} JSON files to process...")
    
    for json_file in json_files:
        file_path = books_folder / json_file
        
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            # Extract book information
            book_number = book_data.get('book_number', 'Unknown')
            english_name = book_data.get('english_name', 'Unknown')
            
            print(f"Processing {json_file} - Book {book_number}: {english_name}")
            
            # Extract content from each hadith
            if 'hadiths' in book_data:
                for i, hadith in enumerate(book_data['hadiths'], 1):
                    if 'content' in hadith:
                        content_entry = {
                            'book_number': book_number,
                            'book_name': english_name,
                            'hadith_number': i,
                            'content': hadith['content']
                        }
                        all_content.append(content_entry)
            
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    # Create the output JSON file
    output_data = {
        'total_hadiths': len(all_content),
        'extracted_date': '2025-08-12',
        'source': 'Muwatta Malik Modified Collection',
        'hadith_contents': all_content
    }
    
    # Save to output file
    output_file = 'all_hadith_contents.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Successfully extracted content from {len(all_content)} hadiths")
    print(f"📁 Output saved to: {output_file}")
    
    return output_file

def extract_content_only():
    """
    Alternative function to extract only the content strings without metadata
    """
    books_folder = Path("Muwatta_Malik_Modified")
    content_list = []
    
    json_files = sorted([f for f in os.listdir(books_folder) if f.endswith('.json')])
    
    for json_file in json_files:
        file_path = books_folder / json_file
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                book_data = json.load(f)
            
            if 'hadiths' in book_data:
                for hadith in book_data['hadiths']:
                    if 'content' in hadith:
                        content_list.append(hadith['content'])
                        
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    # Save just the content strings
    output_file = 'hadith_contents_only.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content_list, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Extracted {len(content_list)} content strings to {output_file}")
    return output_file

if __name__ == "__main__":
    print("🚀 Starting Hadith Content Extraction...")
    print("=" * 50)
    
    # Extract with metadata
    print("\n1. Extracting content with metadata...")
    extract_all_hadith_content()
    
    # Extract content only
    print("\n2. Extracting content only...")
    extract_content_only()
    
    print("\n🎉 All extraction tasks completed!")
