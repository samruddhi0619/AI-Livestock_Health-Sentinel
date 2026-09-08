# Database Management (`database/`)

This directory houses the schema definitions, migrations, and seed scripts for the PostgreSQL + PostGIS database.

## Schema Structure
- `schema.sql`: Full DDL script creating tables, foreign keys, constraints, and spatial indexes (`GIST`) for spatial points and polygons.
- `seed_demo.sql`: Pre-populated hackathon demo accounts, farms, and system configuration records.

## PostgreSQL + PostGIS Setup (Docker)

To run a production-grade PostGIS database container locally:

```bash
docker run --name sentinel-postgis \
  -e POSTGRES_USER=sentinel_user \
  -e POSTGRES_PASSWORD=sentinel_secure_password \
  -e POSTGRES_DB=sentinel_db \
  -p 5432:5432 \
  -d postgis/postgis:16-3.4
```

Initialize the schema and seed records:
```bash
psql -h localhost -U sentinel_user -d sentinel_db -f database/schema.sql
psql -h localhost -U sentinel_user -d sentinel_db -f database/seed_demo.sql
```

## Zero-Config Fallback Sandbox Mode
If PostgreSQL is not running or `DATABASE_URL` is omitted, the application automatically uses its local file-based sandbox database (`backend/data/db.json`), ensuring that the system works out-of-the-box on any computer without requiring database installation.
