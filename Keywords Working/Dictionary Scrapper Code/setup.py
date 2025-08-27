#!/usr/bin/env python3
"""
Setup and Installation Script for Quranic Dictionary Scraper

This script will:
1. Check Python version
2. Install required dependencies  
3. Verify Chrome installation
4. Run a simple test to ensure everything works

Run this first before using the scraper.
"""

import subprocess
import sys
import os
import platform

def check_python_version():
    """Check if Python version is adequate"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("❌ ERROR: Python 3.7+ is required")
        print(f"   Current version: {sys.version}")
        print("   Please install Python 3.7+ from https://python.org")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is installed")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to install dependencies: {e}")
        print("   Try running manually: pip install -r requirements.txt")
        return False

def check_chrome():
    """Check if Chrome browser is available"""
    print("\n🌐 Checking Chrome browser...")
    
    system = platform.system().lower()
    chrome_paths = {
        'windows': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ],
        'darwin': [  # macOS
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        ],
        'linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium'
        ]
    }
    
    if system in chrome_paths:
        for path in chrome_paths[system]:
            if os.path.exists(path):
                print(f"✅ Chrome found at: {path}")
                return True
    
    # Try to run chrome command
    try:
        if system == 'windows':
            subprocess.run(['where', 'chrome'], check=True, capture_output=True)
        else:
            subprocess.run(['which', 'google-chrome'], check=True, capture_output=True)
        print("✅ Chrome is available in system PATH")
        return True
    except subprocess.CalledProcessError:
        pass
    
    print("⚠️  WARNING: Chrome browser not found")
    print("   Please install Google Chrome from https://chrome.google.com")
    print("   The scraper will attempt to download ChromeDriver automatically")
    return False

def test_selenium():
    """Test if Selenium can start a browser"""
    print("\n🧪 Testing Selenium WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("   Setting up headless Chrome...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("   Testing navigation...")
        driver.get('https://www.google.com')
        title = driver.title
        driver.quit()
        
        print(f"✅ Selenium test successful (page title: {title})")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Selenium test failed: {e}")
        print("   This may be due to:")
        print("   - Chrome not installed")
        print("   - Network connectivity issues")
        print("   - Antivirus blocking WebDriver")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    dirs = ['scraped_data']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ Created/verified directory: {dir_name}")

def show_usage_examples():
    """Show usage examples"""
    print("\n🚀 Setup Complete! Here's how to use the scraper:")
    print("\n" + "="*60)
    print("USAGE EXAMPLES:")
    print("="*60)
    
    examples = [
        ("Test with limited data", "python main.py --testing --max-keywords 3"),
        ("Resume previous scraping", "python main.py --resume"),
        ("Scrape specific letters", "python main.py --letters A,b,t"),
        ("Complete scraping", "python main.py"),
        ("Analyze scraped data", "python analyze_data.py"),
    ]
    
    for desc, cmd in examples:
        print(f"\n• {desc}:")
        print(f"  {cmd}")
    
    print("\n" + "="*60)
    print("For Windows users, you can also use: run_scraper.bat")
    print("="*60)

def main():
    """Main setup function"""
    print("🔧 Quranic Dictionary Scraper Setup")
    print("="*50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Check Chrome
    chrome_ok = check_chrome()
    
    # Create directories
    if success:
        create_directories()
    
    # Test Selenium (only if Chrome is available)
    if success and chrome_ok:
        if not test_selenium():
            print("\n⚠️  Selenium test failed, but you can still try running the scraper")
            print("   It may work despite the test failure")
    
    print("\n" + "="*50)
    if success:
        print("🎉 Setup completed successfully!")
        show_usage_examples()
    else:
        print("❌ Setup completed with errors")
        print("   Please resolve the issues above before running the scraper")
    
    print("\n💡 TIP: Start with testing mode first:")
    print("   python main.py --testing --max-keywords 3")
    print("="*50)

if __name__ == "__main__":
    main()
