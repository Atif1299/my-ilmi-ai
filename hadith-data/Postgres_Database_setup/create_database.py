#!/usr/bin/env python3
"""
Database Creation Script for Hadith Database
============================================

This script creates the PostgreSQL database for storing Hadith data.
It connects to PostgreSQL server and creates the 'hadith_db' database if it doesn't exist.

Usage:
    python create_database.py

Requirements:
    - PostgreSQL server running
    - psycopg2 library installed
    - Proper database credentials in .env file
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from urllib.parse import urlparse

def create_database():
    """
    Create the hadith_db database if it doesn't exist.
    """
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        return False
    
    # Parse the database URL
    parsed_url = urlparse(database_url)
    
    # Extract connection details
    host = parsed_url.hostname or 'localhost'
    port = parsed_url.port or 5432
    username = parsed_url.username or 'postgres'
    password = parsed_url.password or ''
    target_database = parsed_url.path.lstrip('/') or 'hadith_db'
    
    print(f"🔗 Connecting to PostgreSQL server at {host}:{port}")
    print(f"📝 Creating database: {target_database}")
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database='postgres'  # Connect to default postgres database
        )
        
        # Set autocommit mode for database creation
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create cursor
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (target_database,)
        )
        
        if cursor.fetchone():
            print(f"✅ Database '{target_database}' already exists")
        else:
            # Create the database
            cursor.execute(f'CREATE DATABASE "{target_database}"')
            print(f"✅ Database '{target_database}' created successfully")
        
        # Close connections
        cursor.close()
        conn.close()
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """
    Main function to create the database.
    """
    print("🚀 Starting Database Creation")
    print("=" * 50)
    
    success = create_database()
    
    if success:
        print("\n✅ Database creation completed successfully!")
        print("📋 Next steps:")
        print("   1. Run 'python import_to_postgres.py' to import data")
        print("   2. Run 'python explore_database.py' to explore the data")
    else:
        print("\n❌ Database creation failed!")
        print("📋 Please check:")
        print("   1. PostgreSQL server is running")
        print("   2. Database credentials in .env file are correct")
        print("   3. User has permission to create databases")
        sys.exit(1)

if __name__ == "__main__":
    main()
