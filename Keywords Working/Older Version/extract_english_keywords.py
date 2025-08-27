import json
import os
from pathlib import Path

def extract_english_keywords():
    """
    Extract all nameEnglish keywords from keywords.json file
    and create a new array containing only the English keywords.
    """
    
    # Path to the keywords.json file
    keywords_file = "keywords.json"
    
    if not os.path.exists(keywords_file):
        print(f"❌ Error: {keywords_file} not found in current directory")
        return
    
    try:
        # Read the keywords.json file
        with open(keywords_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📖 Successfully loaded {keywords_file}")
        
        # Extract English keywords
        english_keywords = []
        
        # Check if data is a list or has a 'body' structure
        if isinstance(data, list) and len(data) > 0 and 'body' in data[0]:
            # Navigate through the structure
            body = data[0]['body']
            rows = body.get('rows', [])
            
            print(f"📊 Found {len(rows)} keyword entries to process...")
            
            for row in rows:
                name_english = row.get('nameEnglish', [])
                if name_english:
                    # Add all English keywords from this row
                    for keyword in name_english:
                        if keyword.strip():  # Only add non-empty keywords
                            english_keywords.append(keyword.strip())
        
        elif isinstance(data, list):
            # If it's a direct list of rows
            print(f"📊 Found {len(data)} keyword entries to process...")
            
            for row in data:
                name_english = row.get('nameEnglish', [])
                if name_english:
                    for keyword in name_english:
                        if keyword.strip():
                            english_keywords.append(keyword.strip())
        
        else:
            print("❌ Unexpected data structure in keywords.json")
            return
        
        # Remove duplicates while preserving order
        unique_english_keywords = []
        seen = set()
        for keyword in english_keywords:
            if keyword not in seen:
                unique_english_keywords.append(keyword)
                seen.add(keyword)
        
        print(f"✅ Extracted {len(english_keywords)} total keywords")
        print(f"✅ Found {len(unique_english_keywords)} unique keywords")
        
        # Create output data structure
        output_data = {
            "total_keywords": len(unique_english_keywords),
            "extracted_date": "2025-08-12",
            "source": "keywords.json",
            "english_keywords": unique_english_keywords
        }
        
        # Save the English keywords array to a new file
        output_file = "english_keywords_only.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Also create a simple array version
        simple_output_file = "english_keywords_array.json"
        with open(simple_output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_english_keywords, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Detailed output saved to: {output_file}")
        print(f"📁 Simple array saved to: {simple_output_file}")
        
        # Display first 10 keywords as preview
        print(f"\n🔍 Preview of first 10 keywords:")
        for i, keyword in enumerate(unique_english_keywords[:10], 1):
            print(f"  {i}. {keyword}")
        
        if len(unique_english_keywords) > 10:
            print(f"  ... and {len(unique_english_keywords) - 10} more keywords")
        
        return output_file, simple_output_file
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in {keywords_file}: {str(e)}")
    except Exception as e:
        print(f"❌ Error processing {keywords_file}: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting English Keywords Extraction...")
    print("=" * 50)
    
    result = extract_english_keywords()
    
    if result:
        print("\n🎉 English keywords extraction completed successfully!")
    else:
        print("\n❌ Extraction failed. Please check the file and try again.")
