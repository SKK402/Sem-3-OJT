# Database Setup Guide

This guide will help you set up PostgreSQL for the Product Search API.

## Option 1: Using Docker (Recommended - Easiest)

### Step 1: Start PostgreSQL Container

```bash
docker run --name postgres-products \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=products \
  -p 5432:5432 \
  -d postgres:15
```

**Windows PowerShell:**
```powershell
docker run --name postgres-products -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=products -p 5432:5432 -d postgres:15
```

This will:
- Create a container named `postgres-products`
- Set the password to `postgres`
- Create a database named `products`
- Expose PostgreSQL on port 5432

### Step 2: Verify Container is Running

```bash
docker ps
```

You should see the `postgres-products` container running.

### Step 3: Configure Environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/products
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=120
MAX_PAGE_SIZE=50
DEFAULT_PAGE_SIZE=12
```

### Step 4: Run Migrations

```bash
alembic upgrade head
```

### Step 5: Seed Sample Data

```bash
python -m app.db.seed
```

---

## Option 2: Local PostgreSQL Installation

### Step 1: Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Or use Chocolatey: `choco install postgresql`

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Create Database

**Windows (using psql):**
```powershell
# Open psql (usually in PostgreSQL installation folder)
psql -U postgres

# Then in psql:
CREATE DATABASE products;
\q
```

**macOS/Linux:**
```bash
sudo -u postgres psql
CREATE DATABASE products;
\q
```

### Step 3: Configure Environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/products
REDIS_URL=redis://localhost:6379/0
```

**Note:** Replace `YOUR_PASSWORD` with your PostgreSQL password.

### Step 4: Run Migrations

```bash
alembic upgrade head
```

### Step 5: Seed Sample Data

```bash
python -m app.db.seed
```

---

## Option 3: Using SQLite (For Development/Testing)

If you want to use SQLite instead of PostgreSQL for quick testing:

### Step 1: Update `.env` file

```env
DATABASE_URL=sqlite+aiosqlite:///./products.db
REDIS_URL=redis://localhost:6379/0
```

**Note:** You'll need to install `aiosqlite`:
```bash
pip install aiosqlite
```

### Step 2: Run Migrations

```bash
alembic upgrade head
```

### Step 3: Seed Sample Data

```bash
python -m app.db.seed
```

---

## Verifying Database Setup

### Check Connection

You can test the database connection by running:

```python
python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Check Tables

Connect to PostgreSQL and verify:

```bash
# Using Docker
docker exec -it postgres-products psql -U postgres -d products

# Or locally
psql -U postgres -d products
```

Then in psql:
```sql
\dt          -- List all tables
\d products  -- Describe products table
SELECT COUNT(*) FROM products;  -- Check if data exists
```

---

## Common Issues & Solutions

### Issue: "Connection refused" or "Can't connect to database"

**Solution:**
1. Verify PostgreSQL is running:
   ```bash
   # Docker
   docker ps
   
   # Local
   # Windows: Check Services
   # macOS/Linux: sudo systemctl status postgresql
   ```

2. Check the connection string in `.env` matches your setup
3. Verify port 5432 is not blocked by firewall

### Issue: "Database does not exist"

**Solution:**
```sql
CREATE DATABASE products;
```

### Issue: "Password authentication failed"

**Solution:**
1. Check your password in `.env` file
2. For Docker, default password is `postgres`
3. For local, reset password:
   ```sql
   ALTER USER postgres PASSWORD 'your_new_password';
   ```

### Issue: "Module 'asyncpg' not found"

**Solution:**
```bash
pip install asyncpg
```

### Issue: Migration errors

**Solution:**
1. Drop and recreate database:
   ```sql
   DROP DATABASE products;
   CREATE DATABASE products;
   ```

2. Run migrations again:
   ```bash
   alembic upgrade head
   ```

---

## Database Management Commands

### View Migration History
```bash
alembic history
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Rollback Migration
```bash
alembic downgrade -1
```

### Reset Database (DANGER: Deletes all data)
```bash
alembic downgrade base
alembic upgrade head
python -m app.db.seed
```

---

## Production Considerations

For production:
1. Use strong passwords
2. Enable SSL connections
3. Use connection pooling
4. Set up database backups
5. Monitor database performance
6. Use environment-specific `.env` files (never commit `.env` to git)

---

## Quick Start Summary

**Using Docker (Fastest):**
```bash
# 1. Start PostgreSQL
docker run --name postgres-products -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=products -p 5432:5432 -d postgres:15

# 2. Create .env file
echo "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/products" > .env

# 3. Run migrations
alembic upgrade head

# 4. Seed data
python -m app.db.seed

# 5. Start API
uvicorn app.main:app --reload
```

That's it! Your database is ready to use.

