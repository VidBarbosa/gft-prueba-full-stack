import os
import sys
from pathlib import Path
import psycopg2

def env(key: str, default: str) -> str:
    return os.getenv(key, default)

def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()

def execute_sql(conn, sql: str):
    with conn.cursor() as cur:
        cur.execute(sql)

def run_sql_file(conn, file_path: Path, visited: set):
    """Soporta `\i path.sql` recursivo (evita ciclos con 'visited')."""
    if file_path in visited:
        return
    visited.add(file_path)

    content = read_text(file_path)
    lines = content.splitlines()

    current_block: list[str] = []

    def flush_block():
        if current_block:
            sql = "\n".join(current_block).strip()
            if sql:
                execute_sql(conn, sql)
            current_block.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            current_block.append(raw)  
            continue

        if line.startswith("\\i "):
            flush_block()
            include_path = line[3:].strip()
            include_file = (file_path.parent / include_path).resolve()
            if not include_file.exists():
                raise FileNotFoundError(f"No se encontró el include: {include_file}")
            run_sql_file(conn, include_file, visited)
        else:
            current_block.append(raw)

    flush_block()

def main():
    run_all = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sql/run_all.sql")
    if not run_all.exists():
        print(f"❌ No se encuentra {run_all}")
        sys.exit(1)

    conn = psycopg2.connect(
        host=env("PGHOST", "localhost"),
        port=int(env("PGPORT", "5432")),
        user=env("PGUSER", "btg"),
        password=env("PGPASSWORD", "btg123"),
        dbname=env("PGDATABASE", "BTG"),
    )
    try:
        with conn:
            run_sql_file(conn, run_all.resolve(), visited=set())
        print("✅ run_all.sql ejecutado correctamente.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
