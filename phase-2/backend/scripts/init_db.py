#!/usr/bin/env python
"""
Database Initialization Script

This script initializes the database schema by creating all tables
defined in the SQLModel models.

Usage:
    python backend/scripts/init_db.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir.parent.parent))

from backend.src.db.session import init_db, engine
from backend.src.config import settings


async def main():
    """Initialize database schema"""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    print()

    # Display connection info
    print("📊 Database Configuration:")
    print("-" * 60)

    # Extract and display connection details (without password)
    db_url = settings.DATABASE_URL
    if ":" in db_url:
        # Extract user@host/db from connection string
        try:
            parts = db_url.split("://")[1].split("@")
            user = parts[0].split(":")[0]
            host_db = parts[1].split("/")
            host = host_db[0]
            db_name = host_db[1].split("?")[0]

            print(f"  User: {user}")
            print(f"  Host: {host}")
            print(f"  Database: {db_name}")
            print(f"  Environment: {settings.ENVIRONMENT}")
        except:
            print("  (Could not parse connection string)")

    print()
    print("🔄 Initializing database schema...")
    print("-" * 60)

    try:
        # Initialize database
        await init_db()
        print("✅ Database initialization completed successfully!")
        print()
        print("📋 Tables created:")
        print("  • users")
        print("  • tasks")
        print()
        print("✨ Schema is ready for use!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"❌ Database initialization failed!")
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  • Check DATABASE_URL in .env.local")
        print("  • Verify Neon database is accessible")
        print("  • Ensure connection string includes ?sslmode=require")
        print("  • Check network connectivity to Neon")
        print("=" * 60)
        return 1

    finally:
        # Close engine connection
        await engine.dispose()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
