# Configuration file for Quranic Dictionary Scraper
import os

# Base URL and endpoints
BASE_URL = "https://corpus.quran.com"
DICTIONARY_URL = f"{BASE_URL}/qurandictionary.jsp"

# Arabic letters mapping (letter symbol to URL parameter)
ARABIC_LETTERS = {
    'أ': 'A',  # Alif
    'ب': 'b',  # Ba
    'ت': 't',  # Ta
    'ث': 'v',  # Tha
    'ج': 'j',  # Jim
    'ح': 'H',  # Ha
    'خ': 'x',  # Kha
    'د': 'd',  # Dal
    'ذ': '*',  # Dhal
    'ر': 'r',  # Ra
    'ز': 'z',  # Zay
    'س': 's',  # Sin
    'ش': '$',  # Shin
    'ص': 'S',  # Sad
    'ض': 'D',  # Dad
    'ط': 'T',  # Ta
    'ظ': 'Z',  # Zah
    'ع': 'E',  # Ain
    'غ': 'g',  # Ghain
    'ف': 'f',  # Fa
    'ق': 'q',  # Qaf
    'ك': 'k',  # Kaf
    'ل': 'l',  # Lam
    'م': 'm',  # Mim
    'ن': 'n',  # Nun
    'ه': 'h',  # Ha
    'و': 'w',  # Waw
    'ي': 'y'   # Ya
}

# Scraping settings
DELAY_BETWEEN_REQUESTS = 2  # seconds
DELAY_BETWEEN_KEYWORDS = 1  # seconds
MAX_RETRIES = 3
TIMEOUT = 30

# Testing mode settings
TESTING_MODE = False  # Set to True for testing with limited data
MAX_LETTERS_FOR_TESTING = 2  # Only process first N letters in testing mode
MAX_KEYWORDS_PER_LETTER = 5  # Only process first N keywords per letter in testing mode

# Output settings
OUTPUT_DIR = "scraped_data"
PROGRESS_FILE = "scraping_progress.json"
SAVE_PROGRESS_INTERVAL = 10  # Save progress every N keywords

# Chrome WebDriver settings
CHROME_OPTIONS = [
    "--headless",  # Run in background
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(OUTPUT_DIR, "scraper.log")
