# Muwatta Malik Database Import

This directory contains scripts to import all Muwatta Malik JSON files into a PostgreSQL database.

## Prerequisites

1. **PostgreSQL Database**: Make sure you have PostgreSQL installed and running
2. **Python Environment**: Python 3.7+ with required packages

## Setup Instructions

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```


### Option 1 :
### 2. Configure Database Connection

Edit the `.env` file with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/your_database_name
```

Example:
```env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/hadith_db
```

### 3. Create Database (if needed)

Connect to PostgreSQL and create the database:

```sql
CREATE DATABASE hadith_db;
```

### Option 2 : 


#### Docker Commands for postgress
```
docker run --name hadith-postgres -e POSTGRES_PASSWORD=ranaatif -e POSTGRES_DB=hadith_db -p 5432:5432 -d postgres:15
```

# Stop the database
```
docker stop hadith-postgres
```

# Start it again
```
docker start hadith-postgres
```
# Remove it completely (if needed)
```
docker rm -f hadith-postgres
```
## Usage

### Import Data to Database

Run the import script:

```bash
python import_to_postgres.py
```

You'll be prompted to choose:
1. **Original books** - Import from `Muwatta Malik/` directory
2. **Modified books** - Import from `Muwatta_Malik_Modified/` directory (includes narrator information)
3. **Both** - Import from both directories
4. **Show stats only** - Display current database statistics

### Query the Database

Use the query utilities:

```bash
python query_database.py
```

This will show:
- Database statistics
- Available books
- Search examples
- Random hadith sample

## Database Schema

### Books Table
- `id` (Primary Key)
- `book_number` (Unique)
- `english_name`
- `arabic_name`
- `created_at`
- `updated_at`

### Hadiths Table
- `id` (Primary Key)
- `book_id` (Foreign Key to Books)
- `english_text`
- `arabic_text`
- `references` (JSON)
- `narrators` (JSON, optional)
- `content` (Text, optional - processed content)
- `created_at`
- `updated_at`

## File Structure

```
web-scrapper/
├── Muwatta Malik/           # Original JSON files
│   ├── book_1.json
│   ├── book_2.json
│   └── ...
├── Muwatta_Malik_Modified/  # Modified files with narrator info
│   ├── book_6.json
│   └── ...
├── database_config.py       # Database connection configuration
├── hadith_models.py         # SQLAlchemy models
├── import_to_postgres.py    # Main import script
├── query_database.py        # Query utilities and examples
├── requirements.txt         # Python dependencies
├── .env                     # Database credentials
└── README.md               # This file
```

## Query Examples

The `HadithQueryManager` class provides various methods:

```python
from query_database import HadithQueryManager

with HadithQueryManager() as hqm:
    # Get all books
    books = hqm.get_all_books()
    
    # Search hadiths
    results = hqm.search_hadiths_by_text("prayer", language="english", limit=5)
    
    # Get hadiths from specific book
    book_hadiths = hqm.get_hadiths_by_book("1", limit=10)
    
    # Get random hadith
    random_hadith = hqm.get_random_hadith()
    
    # Get database stats
    stats = hqm.get_database_stats()
```

## Features

- ✅ **Automatic table creation**
- ✅ **Duplicate prevention** (books won't be imported twice)
- ✅ **JSON field support** for references and narrators
- ✅ **Full-text search** capabilities
- ✅ **Batch import** of all JSON files
- ✅ **Database statistics** and monitoring
- ✅ **Error handling** and progress tracking

## Troubleshooting

1. **Connection Error**: Check your database credentials in `.env`
2. **Import Permission Error**: Ensure PostgreSQL user has CREATE privileges
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **Empty Results**: Verify JSON files exist in the specified directories

## Notes

- The script handles both original and modified JSON files
- Narrator information is stored as JSON for flexible querying
- All timestamps are automatically managed
- The database schema supports future extensions
- Text search is case-insensitive
