# database\seed.py
import sqlite3

def seed_database(db_path, seed_sql_path):
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            cur = conn.cursor()
            
            with open(seed_sql_path, 'rt') as seed_sql:
                seed = seed_sql.read()
        
            cur.executescript(seed)
                                        
            print("Seeded Successfully")
    except Exception as e:
        print (e)
    
    finally:
        conn.close()
seed_database("instance/store.db","database/seed.sql")