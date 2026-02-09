#!/usr/bin/env python3
"""
Manual Database Schema Initialization
Run this script directly to create tables in Neon
"""
import asyncio
import sys
import os
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

async def init_schema():
    """Initialize database schema"""
    print("=" * 80)
    print("MANUAL DATABASE SCHEMA INITIALIZATION")
    print("=" * 80)
    print()

    # Step 1: Load environment
    from dotenv import load_dotenv
    load_dotenv(".env.local")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ ERROR: DATABASE_URL not found in .env.local")
        return False

    print("Step 1: Database Configuration")
    print("-" * 80)
    print(f"  Database: {db_url.split('/')[-1].split('?')[0]}")
    print(f"  Host: {db_url.split('@')[1].split('/')[0]}")
    print()

    try:
        # Step 2: Import required modules
        print("Step 2: Loading SQLModel...")
        print("-" * 80)

        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlmodel import SQLModel
        from backend.src.models.user import User
        from backend.src.models.task import Task

        print("  ✅ SQLModel loaded")
        print(f"  ✅ User model loaded")
        print(f"  ✅ Task model loaded")
        print()

        # Step 3: Create async engine
        print("Step 3: Creating Database Connection...")
        print("-" * 80)

        async_url = db_url.replace("postgresql://", "postgresql+psycopg://")
        engine = create_async_engine(
            async_url,
            echo=True,  # Show SQL statements
            future=True,
        )

        print("  ✅ Async engine created")
        print()

        # Step 4: Create tables
        print("Step 4: Creating Tables...")
        print("-" * 80)

        async with engine.begin() as conn:
            print("  Executing: CREATE TABLE IF NOT EXISTS users...")
            print("  Executing: CREATE TABLE IF NOT EXISTS tasks...")
            await conn.run_sync(SQLModel.metadata.create_all)

        print()
        print("  ✅ Tables created successfully!")
        print()

        # Step 5: Verify tables
        print("Step 5: Verifying Tables...")
        print("-" * 80)

        from sqlalchemy import text

        async with engine.begin() as conn:
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
            ))
            tables = [row[0] for row in result.fetchall()]

            if tables:
                for table in tables:
                    print(f"  ✅ {table}")
            else:
                print("  ❌ No tables found!")
                await engine.dispose()
                return False

        print()

        # Step 6: Check indexes
        print("Step 6: Verifying Indexes...")
        print("-" * 80)

        async with engine.begin() as conn:
            result = await conn.execute(text(
                "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY indexname;"
            ))
            indexes = [row[0] for row in result.fetchall()]

            if indexes:
                for idx in indexes:
                    print(f"  ✅ {idx}")
            else:
                print("  ⚠️  No indexes found")

        await engine.dispose()

        print()
        print("=" * 80)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 80)
        print()
        print("You can now:")
        print("  1. Start the backend:")
        print("     cd backend")
        print("     python -m uvicorn src.main:app --reload")
        print()
        print("  2. Start the frontend:")
        print("     cd frontend")
        print("     npm run dev")
        print()
        print("  3. Open browser: http://localhost:3000")
        print()

        return True

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  • Check .env.local exists and has DATABASE_URL")
        print("  • Check network connectivity to Neon")
        print("  • Verify connection string is correct")
        print("  • Check credentials (user/password)")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        # Try to install python-dotenv if missing
        try:
            import dotenv
        except ImportError:
            print("Installing python-dotenv...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])

        success = asyncio.run(init_schema())
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
