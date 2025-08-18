"""
Interactive Database Explorer
Hands-on tool to explore your Muwatta Malik hadith database
"""

from query_database import HadithQueryManager
import json

def main_menu():
    """Display main menu options"""
    print("\n" + "="*50)
    print("🕌 MUWATTA MALIK HADITH DATABASE EXPLORER")
    print("="*50)
    print("1. 📊 Database Statistics")
    print("2. 📚 Browse All Books")
    print("3. 🔍 Search Hadiths by Keyword")
    print("4. 📖 Explore Specific Book")
    print("5. 👥 Find Hadiths by Narrator")
    print("6. 🆔 Get Specific Hadith by ID")
    print("7. ❌ Exit")
    print("-" * 50)

def show_statistics():
    """Show database statistics"""
    print("\n📊 DATABASE STATISTICS")
    print("=" * 30)
    
    with HadithQueryManager() as db:
        # Total books and hadiths
        books = db.get_all_books()
        total_hadiths = db.get_total_hadith_count()
        
        print(f"📚 Total Books: {len(books)}")
        print(f"📜 Total Hadiths: {total_hadiths}")
        
        # Show book distribution
        print(f"\n📈 HADITHS PER BOOK (Top 10):")
        book_counts = []
        for book in books:
            count = db.get_hadith_count_by_book(book.book_number)
            book_counts.append((book.book_number, book.english_name, count))
        
        # Sort by hadith count descending
        book_counts.sort(key=lambda x: x[2], reverse=True)
        
        for i, (book_num, name, count) in enumerate(book_counts[:10], 1):
            print(f"{i:2d}. Book {book_num}: {name[:40]:<40} ({count} hadiths)")

def browse_books():
    """Browse all books"""
    print("\n📚 ALL BOOKS IN DATABASE")
    print("=" * 40)
    
    with HadithQueryManager() as db:
        books = db.get_all_books()
        
        for book in books:
            hadith_count = db.get_hadith_count_by_book(book.book_number)
            print(f"📖 Book {book.book_number}: {book.english_name}")
            print(f"   Arabic: {book.arabic_name}")
            print(f"   Hadiths: {hadith_count}")
            print()

def search_hadiths():
    """Search hadiths by keyword"""
    keyword = input("\n🔍 Enter search keyword: ").strip()
    if not keyword:
        print("❌ Please enter a keyword!")
        return
    
    print(f"\n🔍 SEARCH RESULTS for '{keyword}'")
    print("=" * 50)
    
    with HadithQueryManager() as db:
        results = db.search_hadiths_by_text(keyword, limit=10)
        
        if not results:
            print(f"❌ No hadiths found containing '{keyword}'")
            return
        
        print(f"📊 Found {len(results)} results (showing first 10):")
        print()
        
        for hadith in results:
            print(f"📜 Hadith {hadith.id} (Book {hadith.book.book_number})")
            print(f"📖 Book: {hadith.book.english_name}")
            
            # Show snippet of text
            english_snippet = hadith.english_text[:200] + "..." if len(hadith.english_text) > 200 else hadith.english_text
            print(f"📝 English: {english_snippet}")
            
            if hadith.arabic_text:
                arabic_snippet = hadith.arabic_text[:100] + "..." if len(hadith.arabic_text) > 100 else hadith.arabic_text
                print(f"🔤 Arabic: {arabic_snippet}")
            
            print(f"📚 Reference: {hadith.references}")
            print("-" * 40)

def explore_book():
    """Explore specific book"""
    try:
        book_num = int(input("\n📖 Enter book number (1-61): "))
        if book_num < 1 or book_num > 61:
            print("❌ Please enter a valid book number (1-61)")
            return
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    with HadithQueryManager() as db:
        book = db.get_book_by_number(str(book_num))
        if not book:
            print(f"❌ Book {book_num} not found")
            return
        
        hadiths = db.get_hadiths_by_book(str(book_num))
        
        print(f"\n📖 BOOK {book_num}: {book.english_name}")
        print("=" * 60)
        print(f"Arabic Name: {book.arabic_name}")
        print(f"Total Hadiths: {len(hadiths)}")
        print()
        
        # Show first few hadiths
        show_count = min(3, len(hadiths))
        print(f"📜 First {show_count} hadiths:")
        print()
        
        for hadith in hadiths[:show_count]:
            print(f"--- HADITH {hadith.id} ---")
            english_snippet = hadith.english_text[:300] + "..." if len(hadith.english_text) > 300 else hadith.english_text
            print(f"English: {english_snippet}")
            print()

def find_by_narrator():
    """Find hadiths by narrator"""
    narrator = input("\n👥 Enter narrator name: ").strip()
    if not narrator:
        print("❌ Please enter a narrator name!")
        return
    
    print(f"\n👥 HADITHS WITH NARRATOR '{narrator}'")
    print("=" * 50)
    
    with HadithQueryManager() as db:
        results = db.search_hadiths_by_narrator(narrator, limit=5)
        
        if not results:
            print(f"❌ No hadiths found with narrator '{narrator}'")
            print("\n💡 Try common narrator names like:")
            print("   - Malik")
            print("   - Yahya")
            print("   - Abdullah")
            print("   - Umar")
            return
        
        print(f"📊 Found {len(results)} results (showing first 5):")
        print()
        
        for hadith in results:
            print(f"📜 Hadith {hadith.id} (Book {hadith.book.book_number})")
            print(f"📖 Book: {hadith.book.english_name}")
            
            # Show narrator chain if available
            if hadith.narrators:
                try:
                    narrators_data = json.loads(hadith.narrators) if isinstance(hadith.narrators, str) else hadith.narrators
                    print(f"👥 Narrators: {narrators_data}")
                except:
                    print(f"👥 Narrators: {hadith.narrators}")
            
            english_snippet = hadith.english_text[:200] + "..." if len(hadith.english_text) > 200 else hadith.english_text
            print(f"📝 Text: {english_snippet}")
            print("-" * 40)

def get_specific_hadith():
    """Get specific hadith by ID"""
    try:
        hadith_id = int(input("\n🆔 Enter hadith ID: "))
    except ValueError:
        print("❌ Please enter a valid number")
        return
    
    with HadithQueryManager() as db:
        hadith = db.get_hadith_by_id(hadith_id)
        
        if not hadith:
            print(f"❌ Hadith with ID {hadith_id} not found")
            return
        
        print(f"\n📜 HADITH {hadith.id}")
        print("=" * 50)
        print(f"📖 Book {hadith.book.book_number}: {hadith.book.english_name}")
        print(f"🔤 Arabic Book: {hadith.book.arabic_name}")
        print()
        print("📝 ENGLISH TEXT:")
        print(hadith.english_text)
        print()
        
        if hadith.arabic_text:
            print("🔤 ARABIC TEXT:")
            print(hadith.arabic_text)
            print()
        
        print(f"📚 References: {hadith.references}")
        
        if hadith.narrators:
            print(f"👥 Narrators: {hadith.narrators}")

def main():
    """Main interactive loop"""
    print("🕌 Welcome to Muwatta Malik Hadith Database Explorer!")
    print("This tool helps you explore your imported hadith collection.")
    
    while True:
        main_menu()
        
        try:
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                show_statistics()
            elif choice == '2':
                browse_books()
            elif choice == '3':
                search_hadiths()
            elif choice == '4':
                explore_book()
            elif choice == '5':
                find_by_narrator()
            elif choice == '6':
                get_specific_hadith()
            elif choice == '7':
                print("\n👋 Thank you for exploring the database!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
