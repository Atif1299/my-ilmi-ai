# Quranic Arabic Dictionary Scraper

A comprehensive Python scraper for extracting the complete Quranic Arabic dictionary from [corpus.quran.com](https://corpus.quran.com/qurandictionary.jsp).

## Features

- **Complete Dictionary Scraping**: Extracts all Arabic letters, keywords, descriptions, and Quranic verse occurrences
- **Morphological Variations**: Captures different forms of each keyword as they appear in verses
- **Progress Tracking**: Resume scraping from where you left off
- **Data Export**: Multiple export formats (JSON, CSV, Markdown reports)
- **Error Handling**: Robust error handling and retry mechanisms
- **Configurable**: Flexible configuration for testing and production use

## What Gets Scraped

For each Arabic letter (أ, ب, ت, etc.):
1. **All keywords** from the dropdown list
2. **Complete descriptions** of each keyword's meaning
3. **Word types** (noun, verb, proper noun, etc.)
4. **All Quranic verses** where the keyword appears
5. **Morphological variations** in Arabic and transliteration
6. **Verse references** with exact locations (Surah:Verse:Word)
7. **English translations** of each occurrence

## Project Structure

```
Keywords Working/
├── main.py              # Main scraping script
├── config.py            # Configuration settings
├── scraper.py           # Core scraping logic
├── webdriver_manager.py # WebDriver management
├── utils.py             # Utility functions
├── analyze_data.py      # Data analysis and export
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── scraped_data/       # Output directory (created automatically)
    ├── complete_quran_dictionary.json
    ├── keywords.csv
    ├── occurrences.csv
    ├── scraping_summary.json
    └── letter_*.json
```

## Installation

1. **Clone or download** the project files to your local machine

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome browser** (if not already installed)
   - The scraper uses Chrome WebDriver which will be automatically downloaded

## Usage

### Basic Usage

Run the complete scraper:
```bash
python main.py
```

### Testing Mode

Run with limited data for testing:
```bash
python main.py --testing --max-keywords 5
```

### Resume Scraping

Resume from previous progress:
```bash
python main.py --resume
```

### Scrape Specific Letters

Scrape only specific letters:
```bash
python main.py --letters A,b,t
```

### Command Line Options

- `--testing`: Run in testing mode with limited data
- `--resume`: Resume from last saved progress  
- `--letters A,b,t`: Scrape specific letters (comma-separated)
- `--max-keywords 10`: Limit keywords per letter (for testing)
- `--headless`: Run browser in background (default: True)
- `--delay 2.0`: Delay between requests in seconds

## Data Analysis

After scraping, analyze the data:
```bash
python analyze_data.py
```

This will generate:
- Statistical analysis
- CSV exports
- Letter-wise breakdowns
- Search index
- Comprehensive report

## Configuration

Edit `config.py` to customize:

- **Testing settings**: Limit data for development
- **Delays**: Adjust request timing to be respectful
- **Output paths**: Change where files are saved
- **Browser options**: Modify Chrome settings

## Output Data Structure

### Keywords Data
```json
{
  "letter": "A",
  "keyword_text": "آدَم", 
  "keyword_value": "A^dam",
  "word_type": "Proper noun",
  "meaning": "Adam",
  "description": "The proper noun ādam (آدَم) occurs 25 times in the Quran...",
  "total_occurrences": 25,
  "occurrences": [...]
}
```

### Occurrence Data
```json
{
  "verse_reference": {"surah": 2, "verse": 31, "word": 2},
  "transliteration": "ādama",
  "english_meaning": "Adam", 
  "arabic_text": "وَعَلَّمَ آدَمَ الْأَسْمَاءَ كُلَّهَا...",
  "highlighted_word": "آدَمَ"
}
```

## Features in Detail

### Progress Tracking
- Automatically saves progress every few keywords
- Resume scraping from exact point of interruption
- Tracks completed letters and keywords

### Error Handling
- Retry failed requests automatically
- Skip problematic keywords and continue
- Detailed logging of all operations

### Data Validation
- Validates extracted data structure
- Handles missing or malformed content gracefully
- Reports data quality issues

### Export Options
- **JSON**: Complete structured data
- **CSV**: Spreadsheet-friendly format
- **Individual files**: Separate file per letter
- **Search index**: For quick keyword lookup

## Performance

- **Respectful scraping**: Built-in delays between requests
- **Resume capability**: No need to restart from beginning
- **Memory efficient**: Processes data incrementally
- **Progress reporting**: Real-time status updates

## Troubleshooting

### Chrome WebDriver Issues
If you get WebDriver errors:
1. Ensure Chrome browser is installed and updated
2. Check your internet connection
3. Try running without `--headless` to see browser activity

### Memory Issues
For large datasets:
1. Use `--testing` mode first
2. Process letters one at a time with `--letters`
3. Monitor disk space in output directory

### Network Issues
If requests fail:
1. Check your internet connection
2. Increase delays in `config.py`
3. Use `--delay` option for slower scraping

## Example Output

After running the scraper, you'll have:

1. **Complete dictionary** (`complete_quran_dictionary.json`) - All scraped data
2. **Keywords list** (`keywords.csv`) - Spreadsheet of all keywords  
3. **Occurrences** (`occurrences.csv`) - All verse occurrences
4. **Statistics** (`dictionary_statistics.json`) - Analysis summary
5. **Report** (`scraping_report.md`) - Human-readable summary

## Legal and Ethical Notes

- This scraper is for educational and research purposes
- Respects the website with appropriate delays between requests
- Does not overload the server with rapid requests
- Complies with the site's terms of use

## License

This project is open source. Please use responsibly and ethically.

## Support

For issues or questions:
1. Check the log files in `scraped_data/scraper.log`
2. Review the configuration in `config.py`
3. Try running with `--testing` mode first
