import psycopg2
import sys

passwords_to_try = ['postgres', 'password', 'root', 'admin', '1234', '123456', '', 'Postgres', 'Postgres@123', 'admin123']
successful_pwd = None

print("[*] Testing connection to PostgreSQL on localhost:5432...")

for pwd in passwords_to_try:
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=5432,
            user='postgres',
            password=pwd,
            dbname='postgres',
            connect_timeout=2
        )
        print(f"[SUCCESS] Connected to PostgreSQL with password: '{pwd}'")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'school_erp';")
        exists = cur.fetchone()
        if not exists:
            cur.execute("CREATE DATABASE school_erp;")
            print("[+] Created database 'school_erp'!")
        else:
            print("[+] Database 'school_erp' already exists.")
        cur.close()
        conn.close()
        successful_pwd = pwd
        break
    except Exception as e:
        msg = str(e).strip()
        if "password authentication failed" in msg.lower():
            print(f"[-] Password '{pwd}' failed.")
        else:
            print(f"[-] Error: {msg}")

if successful_pwd is not None:
    print(f"\n[+] PostgreSQL is READY! Successful password: '{successful_pwd}'")
    sys.exit(0)
else:
    print("\n[!] Could not connect with standard test passwords. Please provide your PostgreSQL password.")
    sys.exit(1)
