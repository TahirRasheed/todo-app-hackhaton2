#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot database connection and table creation
"""
import os
import sys
from pathlib import Path

print("=" * 80)
print("DATABASE DIAGNOSTIC TOOL")
print("=" * 80)
print()

# Step 1: Check Python version
print("Step 1: Python Version")
print("-" * 80)
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}")
print()

# Step 2: Check environment variables
print("Step 2: Environment Variables")
print("-" * 80)
env_file = Path(".env.local")
if env_file.exists():
    with open(env_file) as f:
        content = f.read()
        for line in content.split('\n'):
            if line and not line.startswith('#'):
                if 'PASSWORD' in line or 'SECRET' in line:
                    key = line.split('=')[0]
                    print(f"  {key}=***hidden***")
                else:
                    print(f"  {line}")
else:
    print("❌ .env.local not found!")
    print(f"   Expected at: {env_file.absolute()}")

print()

# Step 3: Check dependencies
print("Step 3: Required Dependencies")
print("-" * 80)

dependencies = {
    'fastapi': 'FastAPI',
    'uvicorn': 'Uvicorn',
    'sqlalchemy': 'SQLAlchemy',
    'sqlmodel': 'SQLModel',
    'psycopg': 'psycopg',
    'pydantic': 'Pydantic',
}

missing = []
for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"  ✅ {name}")
    except ImportError:
        print(f"  ❌ {name} - NOT INSTALLED")
        missing.append(module)

if missing:
    print()
    print("  Install missing packages:")
    print(f"    pip install {' '.join(missing)}")

print()

# Step 4: Test database connection
print("Step 4: Test Database Connection")
print("-" * 80)

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL not set in environment!")
    sys.exit(1)

print(f"  Connection string: {db_url[:70]}...")

if missing:
    print("  ⚠️  Cannot test - missing dependencies. Install first:")
    print(f"    pip install {' '.join(missing)}")
else:
    try:
        import asyncio
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        async def test_conn():
            async_url = db_url.replace("postgresql://", "postgresql+psycopg://")
            print(f"  Testing async connection...")

            engine = create_async_engine(async_url, echo=False)
            try:
                async with engine.begin() as conn:
                    result = await conn.execute(text("SELECT version();"))
                    version = result.scalar()
                    print(f"  ✅ Connection successful!")
                    print(f"     PostgreSQL: {version.split(',')[0]}")

                    # Check existing tables
                    result = await conn.execute(text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
                    ))
                    tables = [row[0] for row in result.fetchall()]

                    if tables:
                        print(f"  ✅ Found {len(tables)} table(s): {', '.join(tables)}")
                    else:
                        print(f"  ⚠️  No tables found - need to initialize schema")

                    return True
            except Exception as e:
                print(f"  ❌ Connection failed: {str(e)}")
                return False
            finally:
                await engine.dispose()

        success = asyncio.run(test_conn())
        if not success:
            print()
            print("  Troubleshooting:")
            print("    • Check DATABASE_URL is correct")
            print("    • Check network connectivity to Neon")
            print("    • Check credentials (user/password)")
            print("    • Visit https://console.neon.tech to verify project")

    except Exception as e:
        print(f"  ❌ Error during test: {str(e)}")

print()
print("=" * 80)
print("DIAGNOSTICS COMPLETE")
print("=" * 80)
print()
print("Next steps:")
print("  1. If connection is OK, run: python init_schema.py")
print("  2. Then start backend: python -m uvicorn src.main:app --reload")
print()
