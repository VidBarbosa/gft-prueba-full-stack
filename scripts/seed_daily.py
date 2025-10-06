import subprocess, sys

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    subprocess.check_call(cmd)

if __name__ == "__main__":
    run([sys.executable, "scripts/reset_mongo.py"])
    run([sys.executable, "scripts/seed_all.py"])
    print("✅ Base restaurada con seed de pruebas")
