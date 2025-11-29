# Quick Database Setup

## Fastest Method: Docker

### 1. Start PostgreSQL with Docker

```powershell
docker run --name postgres-products -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=products -p 5432:5432 -d postgres:15
```

### 2. Create `.env` file

Create a file named `.env` in the project root with:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/products
REDIS_URL=redis://localhost:6379/0
```

### 3. Run database migrations

```powershell
alembic upgrade head
```

### 4. Seed sample data

```powershell
python -m app.db.seed
```

### 5. Verify it works

```powershell
uvicorn app.main:app --reload
```

Then visit: http://localhost:8000/docs

---

## That's it! 

Your database is now set up with:
- ✅ Products table created
- ✅ 200 sample products loaded
- ✅ Ready for API testing

---

## Troubleshooting

**If Docker command fails:**
- Make sure Docker Desktop is running
- Check if port 5432 is already in use

**If migration fails:**
- Check your `.env` file exists and has correct DATABASE_URL
- Verify PostgreSQL container is running: `docker ps`

**If seed fails:**
- Make sure migrations ran successfully first
- Check database connection in `.env`

