import requests
from bs4 import BeautifulSoup
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import html
import unicodedata
from datetime import datetime

class EnhancedBukhariScraper:
    """
    Enhanced Bukhari scraper with improved English content extraction
    """
    
    def __init__(self, use_selenium=True):
        self.base_url = "https://sunnah.com"
        self.bukhari_main_url = "https://sunnah.com/bukhari"
        self.use_selenium = use_selenium
        self.output_folder = "../Results/Sahih-al-Bukhari"
        
        # Create output folder
        self.create_output_folder()
        
        # Always initialize requests session as fallback
        self.setup_requests_session()
        
        if use_selenium:
            self.setup_selenium()
        else:
            print("💡 Using requests-only mode")
    
    def create_output_folder(self):
        """Create output folder for all books"""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"📁 Created folder: {self.output_folder}")
        else:
            print(f"📁 Using existing folder: {self.output_folder}")
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Try to find Chrome driver
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Selenium WebDriver initialized")
            
        except Exception as e:
            print(f"❌ Selenium setup failed: {e}")
            print("💡 Falling back to requests-only mode")
            self.use_selenium = False
            self.setup_requests_session()
    
    def setup_requests_session(self):
        """Setup requests session as fallback"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_all_book_numbers(self):
        """Get all book numbers from the main Bukhari page"""
        print(f"🔍 Fetching book list from: {self.bukhari_main_url}")
        
        try:
            response = self.session.get(self.bukhari_main_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all book links
            book_links = soup.find_all('a', href=re.compile(r'/bukhari/\d+'))
            book_numbers = []
            
            for link in book_links:
                href = link.get('href')
                match = re.search(r'/bukhari/(\d+)', href)
                if match:
                    book_num = int(match.group(1))
                    if book_num not in book_numbers:
                        book_numbers.append(book_num)
            
            book_numbers.sort()
            print(f"📚 Found {len(book_numbers)} books: {book_numbers}")
            return book_numbers
            
        except Exception as e:
            print(f"❌ Error fetching book list: {e}")
            # Fallback: assume books 1-97 (standard Bukhari collection)
            fallback_books = list(range(1, 98))
            print(f"🔄 Using fallback book range: 1-97")
            return fallback_books
    
    def get_page_with_language_toggle(self, url, language='english'):
        """Get page content with specific language toggled"""
        if not self.use_selenium:
            # Fallback to simple request
            return self.get_page_content_simple(url)
        
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "actualHadithContainer"))
            )
            
            # Additional wait for JavaScript to fully load
            time.sleep(3)
            
            # Find and click the language radio button
            if language != 'english':
                try:
                    # Try multiple selectors for language toggle
                    language_selectors = [
                        f"#{language}",
                        f"#ch_{language}",
                        f"input[value='{language}']",
                        f"input[id*='{language}']"
                    ]
                    
                    language_radio = None
                    for selector in language_selectors:
                        try:
                            language_radio = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            break
                        except:
                            continue
                    
                    if language_radio:
                        print(f"🔄 Switching to {language}...")
                        self.driver.execute_script("arguments[0].click();", language_radio)
                        
                        # Wait longer for the language toggle to take effect
                        time.sleep(5)
                        
                        # Try to trigger any additional JavaScript functions
                        try:
                            self.driver.execute_script("if(typeof toggleLanguageDisplay === 'function') toggleLanguageDisplay();")
                        except:
                            pass
                    else:
                        print(f"⚠️ Language toggle for {language} not found")
                    
                except Exception as e:
                    print(f"⚠️ Error toggling language: {e}")
            
            # Get page source after language toggle
            page_source = self.driver.page_source
            return page_source
            
        except Exception as e:
            print(f"❌ Error loading page with Selenium: {e}")
            return None
    
    def get_page_content_simple(self, url):
        """Simple page fetch without JavaScript"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def clean_arabic_text(self, text):
        """Clean Arabic text and remove problematic characters"""
        if not text:
            return ""
        
        # Decode HTML entities first
        text = html.unescape(text)
        
        # Remove specific problematic Unicode characters
        problematic_chars = [
            '\u200f',  # Right-to-left mark (‏)
            '\u200e',  # Left-to-right mark
            '\u06d4',  # Arabic full stop (۔)
            '\u202d',  # Left-to-right override
            '\u202c',  # Pop directional formatting
            '\u202a',  # Left-to-right embedding
            '\u202b',  # Right-to-left embedding
        ]
        
        for char in problematic_chars:
            text = text.replace(char, '')
        
        # Clean extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove any remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove any non-printable characters except Arabic text
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in [' ', '\n', '\t'])
        
        return text.strip()
    
    def extract_unified_arabic_content(self, arabic_container):
        """Extract unified Arabic content from the main container"""
        if not arabic_container:
            return ""
        
        try:
            # Remove anchor tags but keep their text content
            for a_tag in arabic_container.find_all('a'):
                a_tag.unwrap()
            
            # Get all text content from the main container in order
            full_arabic_text = arabic_container.get_text(separator=" ", strip=True)
            
            # Clean the text
            cleaned_text = self.clean_arabic_text(full_arabic_text)
            
            return cleaned_text
            
        except Exception as e:
            return ""
    
    def extract_english_content_enhanced(self, hadith_container):
        """Enhanced English content extraction with multiple fallback methods"""
        english_text = ""
        narrator = ""
        
        try:
            # Method 1: Standard English container
            english_container = hadith_container.find('div', class_='englishcontainer')
            if english_container:
                # Extract narrator
                narrator_elem = english_container.find('div', class_='hadith_narrated')
                if narrator_elem:
                    narrator_text = narrator_elem.get_text(strip=True)
                    narrator = re.sub(r'^Narrated\s+', '', narrator_text, flags=re.IGNORECASE)
                
                # Extract English text
                text_details = english_container.find('div', class_='text_details')
                if text_details:
                    # Try to get all paragraphs
                    paragraphs = text_details.find_all('p')
                    if paragraphs:
                        english_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    else:
                        # Fallback: get all text from text_details
                        english_text = text_details.get_text(strip=True)
            
            # Method 2: If no English text found, try alternative selectors
            if not english_text:
                alternative_selectors = [
                    'div.english_hadith_full',
                    'div[class*="english"]',
                    'div.text_details',
                    '.hadith_english'
                ]
                
                for selector in alternative_selectors:
                    elem = hadith_container.select_one(selector)
                    if elem:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 20:  # Ensure meaningful content
                            english_text = text
                            break
            
            # Method 3: Try to extract from any visible text content
            if not english_text:
                # Look for any div that might contain English content
                all_divs = hadith_container.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    # Check if text looks like English (contains common English words)
                    english_indicators = ['the', 'and', 'Allah', 'said', 'Prophet', 'Messenger', 'from', 'that', 'was', 'were']
                    if any(word in text.lower() for word in english_indicators) and len(text) > 30:
                        # Skip if it looks like a narrator line only
                        if not text.lower().startswith('narrated') or len(text) > 50:
                            english_text = text
                            break
            
            return self.clean_text(narrator), self.clean_text(english_text)
            
        except Exception as e:
            print(f"    ⚠️ Error extracting English content: {e}")
            return "", ""
    
    def extract_hadith_with_all_languages_enhanced(self, url, hadith_number):
        """Enhanced hadith extraction with multiple attempts for English content"""
        languages = ['english', 'urdu', 'bangla']
        
        complete_hadith = {
            'hadith_number': hadith_number,
            'narrator': '',
            'english': '',
            'arabic': '',  # Single unified Arabic field
            'urdu': '',
            'bangla': '',
            'references': {}
        }
        
        for language in languages:
            try:
                if self.use_selenium:
                    content = self.get_page_with_language_toggle(url, language)
                else:
                    content = self.get_page_content_simple(url)
                
                if not content:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                hadith_containers = soup.find_all('div', class_='actualHadithContainer')
                
                # Find the specific hadith
                for container in hadith_containers:
                    container_data = self.extract_hadith_from_container_enhanced(container)
                    if container_data.get('hadith_number') == hadith_number:
                        
                        # Merge language-specific data
                        if language == 'english':
                            complete_hadith.update({
                                'narrator': container_data.get('narrator', ''),
                                'english': container_data.get('english', ''),
                                'arabic': container_data.get('arabic', ''),  # Unified Arabic
                                'references': container_data.get('references', {})
                            })
                            
                            # If English is still empty, try enhanced extraction
                            if not complete_hadith['english']:
                                narrator, english_text = self.extract_english_content_enhanced(container)
                                if english_text:
                                    complete_hadith['english'] = english_text
                                if narrator and not complete_hadith['narrator']:
                                    complete_hadith['narrator'] = narrator
                        
                        elif language == 'urdu':
                            urdu_text = self.extract_language_specific_content(container, 'urdu')
                            if urdu_text:
                                complete_hadith['urdu'] = urdu_text
                        elif language == 'bangla':
                            bangla_text = self.extract_language_specific_content(container, 'bangla')
                            if bangla_text:
                                complete_hadith['bangla'] = bangla_text
                        
                        break
                
                # Add delay between language switches
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ Error extracting {language}: {e}")
                continue
        
        return complete_hadith
    
    def extract_language_specific_content(self, container, language):
        """Extract content for a specific language from container"""
        if language == 'urdu':
            selectors = [
                'div.urdu_hadith_full',
                'div.urducontainer',
                'div[style*="display: block"] .urdu_hadith_full',
                'div[class*="urdu"]:not([style*="display: none"])'
            ]
        elif language == 'bangla':
            selectors = [
                'div.bangla_hadith_full', 
                'div.bengalicontainer',
                'div[style*="display: block"] .bangla_hadith_full',
                'div[class*="bangla"]:not([style*="display: none"])',
                'div[class*="bengali"]:not([style*="display: none"])'
            ]
        else:
            return ""
        
        for selector in selectors:
            try:
                element = container.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        return self.clean_text(text)
            except:
                continue
        
        return ""
    
    def extract_hadith_from_container_enhanced(self, hadith_container):
        """Enhanced hadith data extraction from container"""
        hadith_data = {}
        
        # Extract hadith reference number
        reference_sticky = hadith_container.find('div', class_='hadith_reference_sticky')
        if reference_sticky:
            ref_text = reference_sticky.get_text(strip=True)
            hadith_number = re.search(r'Sahih al-Bukhari (\d+)', ref_text)
            if hadith_number:
                hadith_data['hadith_number'] = hadith_number.group(1)
        
        # Enhanced English content extraction
        narrator, english_text = self.extract_english_content_enhanced(hadith_container)
        hadith_data['narrator'] = narrator
        hadith_data['english'] = english_text
        
        # Extract unified Arabic content
        arabic_container = hadith_container.find('div', class_='arabic_hadith_full arabic')
        if arabic_container:
            unified_arabic = self.extract_unified_arabic_content(arabic_container)
            hadith_data['arabic'] = unified_arabic
        
        # Extract references
        references = {}
        reference_table = hadith_container.find('table', class_='hadith_reference')
        if reference_table:
            rows = reference_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).replace(':', '')
                    value = cells[1].get_text(strip=True).replace(':', '').strip()
                    if key and value:
                        references[key] = value
        
        hadith_data['references'] = references
        
        return hadith_data
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_book_info(self, soup):
        """Extract book information"""
        book_info = {}
        
        book_page_title = soup.find('div', class_='book_page_colindextitle')
        if book_page_title:
            arabic_name_elem = book_page_title.find('div', class_='book_page_arabic_name arabic')
            if arabic_name_elem:
                arabic_name = arabic_name_elem.get_text(strip=True)
                book_info['arabic_name'] = self.clean_arabic_text(arabic_name)
            
            book_number_elem = book_page_title.find('div', class_='book_page_number')
            if book_number_elem:
                book_info['book_number'] = book_number_elem.get_text(strip=True).replace('&nbsp;', '').strip()
            
            english_name_elem = book_page_title.find('div', class_='book_page_english_name')
            if english_name_elem:
                book_info['english_name'] = english_name_elem.get_text(strip=True)
        
        return book_info
    
    def scrape_single_book(self, book_number):
        """Scrape a single book with all hadiths"""
        url = f"{self.base_url}/bukhari/{book_number}"
        print(f"\n📖 SCRAPING BOOK {book_number}")
        print(f"🌐 URL: {url}")
        
        # First get the page to identify hadiths
        content = self.get_page_content_simple(url)
        if not content:
            print(f"❌ Failed to fetch Book {book_number}")
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        book_info = self.extract_book_info(soup)
        
        # Get hadith numbers
        hadith_containers = soup.find_all('div', class_='actualHadithContainer')
        hadith_numbers = []
        
        for container in hadith_containers:
            container_data = self.extract_hadith_from_container_enhanced(container)
            if container_data.get('hadith_number'):
                hadith_numbers.append(container_data['hadith_number'])
        
        total_hadiths = len(hadith_numbers)
        print(f"📊 Found {total_hadiths} hadiths in Book {book_number}")
        
        if total_hadiths == 0:
            print(f"⚠️ No hadiths found in Book {book_number}, skipping...")
            return None
        
        # Extract each hadith with all languages
        hadiths = []
        failed_english = 0
        
        for i, hadith_num in enumerate(hadith_numbers, 1):
            print(f"  📝 Processing hadith {i}/{total_hadiths} (Bukhari {hadith_num})")
            
            try:
                complete_hadith = self.extract_hadith_with_all_languages_enhanced(url, hadith_num)
                hadiths.append(complete_hadith)
                
                # Show progress and track missing English content
                ar_len = len(complete_hadith.get('arabic', ''))
                en_len = len(complete_hadith.get('english', ''))
                ur_len = len(complete_hadith.get('urdu', ''))
                bn_len = len(complete_hadith.get('bangla', ''))
                
                if en_len == 0:
                    failed_english += 1
                    print(f"    ⚠️ EN({en_len}) AR({ar_len}) UR({ur_len}) BN({bn_len}) - NO ENGLISH")
                else:
                    print(f"    ✅ EN({en_len}) AR({ar_len}) UR({ur_len}) BN({bn_len})")
                
                # Add small delay to be respectful to the server
                time.sleep(1.5)
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        print(f"  📊 Summary: {total_hadiths - failed_english}/{total_hadiths} hadiths have English content")
        if failed_english > 0:
            print(f"  ⚠️ {failed_english} hadiths missing English content")
        
        book_data = {
            "book_number": book_info.get('book_number', str(book_number)),
            "english_name": book_info.get('english_name', ''),
            "arabic_name": book_info.get('arabic_name', ''),
            "total_hadiths": len(hadiths),
            "hadiths_with_english": total_hadiths - failed_english,
            "hadiths_missing_english": failed_english,
            "scraped_at": datetime.now().isoformat(),
            "hadiths": hadiths
        }
        
        return book_data
    
    def save_book_data(self, book_data, book_number):
        """Save book data to JSON file"""
        if not book_data:
            return False
        
        filename = f"book_{book_number:02d}_{book_data.get('english_name', 'Unknown').replace(' ', '_').replace('/', '_')}.json"
        filepath = os.path.join(self.output_folder, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving Book {book_number}: {e}")
            return False
    
    def scrape_all_books(self, start_book=1, end_book=None):
        """Scrape all books in the Bukhari collection"""
        print("🕌 ENHANCED SAHIH AL-BUKHARI SCRAPER")
        print("=" * 70)
        
        # Get all available book numbers
        all_book_numbers = self.get_all_book_numbers()
        
        # Apply range filter if specified
        if end_book:
            all_book_numbers = [num for num in all_book_numbers if start_book <= num <= end_book]
        else:
            all_book_numbers = [num for num in all_book_numbers if num >= start_book]
        
        print(f"📚 Will scrape {len(all_book_numbers)} books: {all_book_numbers}")
        
        successful_books = 0
        failed_books = 0
        total_english_missing = 0
        
        for i, book_num in enumerate(all_book_numbers, 1):
            print(f"\n🔄 PROGRESS: {i}/{len(all_book_numbers)} books")
            
            try:
                book_data = self.scrape_single_book(book_num)
                
                if book_data and self.save_book_data(book_data, book_num):
                    successful_books += 1
                    total_english_missing += book_data.get('hadiths_missing_english', 0)
                    print(f"✅ Book {book_num} completed successfully!")
                else:
                    failed_books += 1
                    print(f"❌ Book {book_num} failed!")
                
                # Add delay between books
                time.sleep(3)
                
            except Exception as e:
                failed_books += 1
                print(f"❌ Book {book_num} failed with error: {e}")
                continue
        
        # Final summary
        print(f"\n🎉 ENHANCED SCRAPING COMPLETED!")
        print(f"✅ Successful books: {successful_books}")
        print(f"❌ Failed books: {failed_books}")
        print(f"⚠️ Total hadiths missing English: {total_english_missing}")
        print(f"📁 Output folder: {os.path.abspath(self.output_folder)}")
        
        # Create summary file
        summary = {
            "scraping_completed_at": datetime.now().isoformat(),
            "total_books_attempted": len(all_book_numbers),
            "successful_books": successful_books,
            "failed_books": failed_books,
            "total_hadiths_missing_english": total_english_missing,
            "scraped_books": all_book_numbers
        }
        
        summary_file = os.path.join(self.output_folder, "enhanced_scraping_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Enhanced summary saved: enhanced_scraping_summary.json")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.use_selenium and hasattr(self, 'driver'):
            self.driver.quit()
            print("🧹 Selenium driver closed")

def main():
    print("🕌 Enhanced Sahih al-Bukhari Collection Scraper")
    print("=" * 70)
    
    scraper = EnhancedBukhariScraper(use_selenium=True)
    
    try:
        print("\nChoose scraping option:")
        print("1. Scrape all books (1-97)")
        print("2. Scrape specific range of books")
        print("3. Test with first 3 books only (enhanced)")
        print("4. Re-scrape Book 1 to test English extraction")
        
        choice = input("Enter choice (1, 2, 3, or 4): ").strip()
        
        if choice == "1":
            scraper.scrape_all_books()
        elif choice == "2":
            start = int(input("Enter start book number: "))
            end = int(input("Enter end book number: "))
            scraper.scrape_all_books(start_book=start, end_book=end)
        elif choice == "3":
            scraper.scrape_all_books(start_book=1, end_book=3)
        elif choice == "4":
            scraper.scrape_all_books(start_book=1, end_book=1)
        else:
            print("Invalid choice, testing enhanced extraction on Book 1...")
            scraper.scrape_all_books(start_book=1, end_book=1)
        
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
