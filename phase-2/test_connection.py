#!/usr/bin/env python3
"""
Test Neon Database Connection
Run this script to verify the connection to Neon PostgreSQL
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

async def test_connection():
    """Test database connection"""
    print("=" * 70)
    print("Testing Neon PostgreSQL Connection")
    print("=" * 70)
    print()

    try:
        # Import after path is set
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        # Connection string
        db_url = "postgresql://neondb_owner:npg_C3u5VxKMPjXR@ep-holy-butterfly-ai4lnkq4-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        async_db_url = db_url.replace("postgresql://", "postgresql+psycopg://")

        print("📊 Connection Details:")
        print("-" * 70)
        print(f"  Database URL: {db_url[:60]}...")
        print(f"  Using psycopg driver: postgresql+psycopg://")
        print()

        print("🔄 Attempting connection...")
        print("-" * 70)

        # Create engine
        engine = create_async_engine(
            async_db_url,
            echo=False,
        )

        # Test connection
        async with engine.begin() as conn:
            # Test 1: Get database version
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print("✅ Connection successful!")
            print(f"   Database: {version[:50]}...")
            print()

            # Test 2: Check existing tables
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            ))
            tables = result.fetchall()
            print("📋 Existing Tables:")
            if tables:
                for (table,) in tables:
                    print(f"   ✓ {table}")
            else:
                print("   ⚠️  No tables found - schema not initialized yet")
            print()

            # Test 3: Test write permission
            try:
                await conn.execute(text("CREATE TEMPORARY TABLE test_write (id INT);"))
                await conn.execute(text("DROP TABLE test_write;"))
                print("✅ Write permission: OK")
            except Exception as e:
                print(f"❌ Write permission: FAILED - {str(e)}")

        await engine.dispose()

        print()
        print("=" * 70)
        print("✅ All tests passed! Connection is working.")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Run the init_tables.sql script to create tables")
        print("2. Start the backend: python -m uvicorn src.main:app --reload")
        print()
        return 0

    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print()
        print("Missing dependencies. Install with:")
        print("  pip install sqlalchemy psycopg")
        print()
        return 1

    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  • Check network connectivity to Neon")
        print("  • Verify DATABASE_URL in .env.local")
        print("  • Check credentials (user/password)")
        print("  • Ensure sslmode=require is set")
        print("  • Visit https://console.neon.tech to verify project exists")
        print()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(test_connection())
    sys.exit(exit_code)
