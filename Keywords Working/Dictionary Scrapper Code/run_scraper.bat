@echo off
echo Quranic Arabic Dictionary Scraper
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install requirements
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

REM Ask user what they want to do
echo What would you like to do?
echo 1. Run complete scraper (all letters)
echo 2. Run in testing mode (limited data)
echo 3. Resume previous scraping
echo 4. Scrape specific letters
echo 5. Analyze existing data
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Running complete scraper...
    python main.py
) else if "%choice%"=="2" (
    echo Running in testing mode...
    python main.py --testing --max-keywords 5
) else if "%choice%"=="3" (
    echo Resuming previous scraping...
    python main.py --resume
) else if "%choice%"=="4" (
    echo.
    echo Available letters: A,b,t,v,j,H,x,d,*,r,z,s,$,S,D,T,Z,E,g,f,q,k,l,m,n,h,w,y
    echo Example: A,b,t (for first 3 letters)
    echo.
    set /p letters="Enter letters to scrape (comma-separated): "
    python main.py --letters %letters%
) else if "%choice%"=="5" (
    echo Analyzing existing data...
    python analyze_data.py
) else (
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

echo.
echo Operation completed! Check the 'scraped_data' folder for results.
echo.
pause
