import os
import sys
from pathlib import Path
from restore_pg import run as restore_run

def main():
    outdir = Path(os.getenv("OUTDIR", "./pg_backups"))
    if not outdir.exists():
        print(f"❌ Carpeta no encontrada: {outdir}")
        sys.exit(1)

    backups = sorted(outdir.glob("*.sql"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        print(f"❌ No hay backups en {outdir}")
        sys.exit(1)

    latest = backups[0]
    print(f"==> Rollback usando: {latest}")
    restore_run(str(latest))

if __name__ == "__main__":
    main()
