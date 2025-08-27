import time
import logging
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from browser_manager import WebDriverManager
from utils import clean_text, extract_verse_reference, safe_log_text
from config import DICTIONARY_URL, DELAY_BETWEEN_KEYWORDS, MAX_RETRIES

class QuranDictionaryScraper:
    """Main scraper class for Quranic Arabic dictionary"""
    
    def __init__(self, driver_manager):
        self.logger = logging.getLogger(__name__)
        self.driver_manager = driver_manager
        
    def get_letter_keywords(self, letter_param):
        """Get all keywords for a specific letter from the dropdown"""
        try:
            # URL encode the letter parameter to handle special characters like $
            encoded_param = urllib.parse.quote(letter_param)
            url = f"{DICTIONARY_URL}?q={encoded_param}"
            
            if not self.driver_manager.navigate_to_url(url):
                return []
            
            # Wait for the dropdown to load
            dropdown_element = self.driver_manager.wait_for_element(By.ID, "entryList")
            if not dropdown_element:
                self.logger.error(f"Dropdown not found for letter {letter_param}")
                return []
            
            # Get all options from dropdown
            dropdown = Select(dropdown_element)
            options = dropdown.options
            
            keywords = []
            for option in options:
                keyword_value = option.get_attribute('value')
                keyword_text = option.text.strip()
                
                if keyword_value and keyword_text:
                    keywords.append({
                        'value': keyword_value,
                        'text': keyword_text,
                        'url_encoded': keyword_value
                    })
            
            self.logger.info(f"Found {len(keywords)} keywords for letter {letter_param}")
            return keywords
            
        except Exception as e:
            self.logger.error(f"Error getting keywords for letter {letter_param}: {e}")
            return []
    
    def scrape_keyword_data(self, letter_param, keyword_info):
        """Scrape complete data for a specific keyword"""
        keyword_data = {
            'letter': letter_param,
            'keyword_value': keyword_info['value'],
            'keyword_text': keyword_info['text'],
            'description': '',
            'word_type': '',
            'meaning': '',
            'occurrences': [],
            'total_occurrences': 0,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Navigate to keyword page
            url = f"{DICTIONARY_URL}?q={keyword_info['url_encoded']}"
            
            if not self.driver_manager.navigate_to_url(url):
                return keyword_data
            
            # Extract description
            keyword_data['description'] = self._extract_description()
            
            # Extract word type and meaning
            word_type, meaning = self._extract_word_type_and_meaning()
            keyword_data['word_type'] = word_type
            keyword_data['meaning'] = meaning
            
            # Extract all occurrences (ayahs)
            keyword_data['occurrences'] = self._extract_occurrences()
            keyword_data['total_occurrences'] = len(keyword_data['occurrences'])
            
            safe_keyword = safe_log_text(keyword_info['text'])
            self.logger.info(f"Scraped keyword '{safe_keyword}' with {keyword_data['total_occurrences']} occurrences")
            
        except Exception as e:
            safe_keyword = safe_log_text(keyword_info['text'])
            self.logger.error(f"Error scraping keyword {safe_keyword}: {e}")
        
        return keyword_data
    
    def _extract_description(self):
        """Extract the main description paragraph"""
        try:
            # Look for the description paragraph with class 'dsm'
            desc_element = self.driver_manager.find_element_safe(By.CSS_SELECTOR, "p.dsm")
            if desc_element:
                return clean_text(desc_element.text)
            
            # Fallback: look for any paragraph that contains keyword description
            paragraphs = self.driver_manager.find_elements_safe(By.TAG_NAME, "p")
            for p in paragraphs:
                text = p.text.strip()
                if "occurs" in text and "times in the Quran" in text:
                    return clean_text(text)
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting description: {e}")
            return ""
    
    def _extract_word_type_and_meaning(self):
        """Extract word type and meaning from h4 elements"""
        try:
            word_type = ""
            meaning = ""
            
            # Look for h4 elements with class 'dxe'
            h4_elements = self.driver_manager.find_elements_safe(By.CSS_SELECTOR, "h4.dxe")
            for h4 in h4_elements:
                text = h4.text.strip()
                if text:
                    if " - " in text:
                        parts = text.split(" - ", 1)
                        word_type = parts[0].strip()
                        meaning = parts[1].strip()
                    else:
                        word_type = text
                    break
            
            return word_type, meaning
            
        except Exception as e:
            self.logger.error(f"Error extracting word type and meaning: {e}")
            return "", ""
    
    def _extract_occurrences(self):
        """Extract all Quranic occurrences of the keyword"""
        occurrences = []
        
        try:
            # Look for the main table containing occurrences
            table = self.driver_manager.find_element_safe(By.CSS_SELECTOR, "table.taf")
            if not table:
                self.logger.warning("No occurrences table found")
                return occurrences
            
            # Get all rows from the table
            rows = self.driver_manager.find_elements_safe(By.TAG_NAME, "tr")
            
            for row in rows:
                try:
                    occurrence = self._parse_occurrence_row(row)
                    if occurrence:
                        occurrences.append(occurrence)
                except Exception as e:
                    self.logger.warning(f"Error parsing occurrence row: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(occurrences)} occurrences")
            
        except Exception as e:
            self.logger.error(f"Error extracting occurrences: {e}")
        
        return occurrences
    
    def _parse_occurrence_row(self, row):
        """Parse a single occurrence row from the table"""
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 3:
                return None
            
            # Extract verse reference from first cell
            ref_cell = cells[0]
            ref_text = ref_cell.text.strip()
            verse_ref = extract_verse_reference(ref_text)
            
            if not verse_ref:
                return None
            
            # Extract transliteration and variation
            ref_elements = ref_cell.find_elements(By.TAG_NAME, "i")
            transliteration = ""
            if ref_elements:
                transliteration = ref_elements[0].text.strip()
            
            # Extract English meaning from second cell
            meaning_cell = cells[1]
            english_meaning = clean_text(meaning_cell.text)
            
            # Extract Arabic text from third cell
            arabic_cell = cells[2]
            arabic_text = clean_text(arabic_cell.text)
            
            # Extract highlighted word (the keyword variation)
            highlighted_elements = arabic_cell.find_elements(By.CSS_SELECTOR, "span.auu")
            highlighted_word = ""
            if highlighted_elements:
                highlighted_word = highlighted_elements[0].text.strip()
            
            return {
                'verse_reference': verse_ref,
                'transliteration': transliteration,
                'english_meaning': english_meaning,
                'arabic_text': arabic_text,
                'highlighted_word': highlighted_word,
            }
            
        except Exception as e:
            self.logger.warning(f"Error parsing occurrence row: {e}")
            return None
    
    def scrape_letter(self, letter, letter_param, max_keywords=None):
        """Scrape all keywords for a specific letter"""
        safe_letter = safe_log_text(letter)
        self.logger.info(f"Starting to scrape letter '{safe_letter}' (param: {letter_param})")
        
        # Get all keywords for this letter
        keywords = self.get_letter_keywords(letter_param)
        if not keywords:
            self.logger.warning(f"No keywords found for letter {safe_letter}")
            return []
        
        # Limit keywords for testing if specified
        if max_keywords:
            keywords = keywords[:max_keywords]
            self.logger.info(f"Limited to {max_keywords} keywords for testing")
        
        letter_data = []
        
        for i, keyword_info in enumerate(keywords, 1):
            try:
                safe_keyword = safe_log_text(keyword_info['text'])
                self.logger.info(f"Scraping keyword {i}/{len(keywords)}: {safe_keyword}")
                
                keyword_data = self.scrape_keyword_data(letter_param, keyword_info)
                letter_data.append(keyword_data)
                
                # Add delay between keywords
                time.sleep(DELAY_BETWEEN_KEYWORDS)
                
            except Exception as e:
                safe_keyword = safe_log_text(keyword_info['text'])
                self.logger.error(f"Error scraping keyword {safe_keyword}: {e}")
                continue
        
        self.logger.info(f"Completed scraping letter '{safe_letter}' with {len(letter_data)} keywords")
        return letter_data
