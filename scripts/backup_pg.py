import os
import subprocess
from datetime import datetime
from pathlib import Path

def env(key: str, default: str) -> str:
    return os.getenv(key, default)

def run():
    db = env("PGDATABASE", "BTG")
    user = env("PGUSER", "btg")
    host = env("PGHOST", "localhost")
    port = env("PGPORT", "5432")
    password = env("PGPASSWORD", "btg123")

    outdir = Path(os.getenv("OUTDIR", "./pg_backups"))
    outdir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    outfile = outdir / f"{db}_backup_{stamp}.sql"

    cmd = [
        "pg_dump",
        "-h", host,
        "-p", port,
        "-U", user,
        "-d", db,
        "-F", "p",
        "-f", str(outfile),
    ]

    env_vars = os.environ.copy()
    env_vars["PGPASSWORD"] = password

    print(f"==> Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=env_vars)
    print(f"✅ Backup creado: {outfile}")

if __name__ == "__main__":
    run()
