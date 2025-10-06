import os
import sys
from pathlib import Path
import psycopg2

def env(key: str, default: str) -> str:
    return os.getenv(key, default)

def load_sql_file(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()

def run(sql_file: str):
    path = Path(sql_file)
    if not path.exists():
        print(f"❌ No existe el archivo: {path}")
        sys.exit(1)

    conn = psycopg2.connect(
        host=env("PGHOST", "localhost"),
        port=int(env("PGPORT", "5432")),
        user=env("PGUSER", "btg"),
        password=env("PGPASSWORD", "btg123"),
        dbname=env("PGDATABASE", "BTG"),
    )
    try:
        sql = load_sql_file(path)
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        print("✅ Restore completado.")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/restore_pg.py <ruta_al_backup.sql>")
        sys.exit(1)
    run(sys.argv[1])
