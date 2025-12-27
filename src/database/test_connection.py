
from sqlalchemy import text
from connection import engine

def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) from address_registry"))
        count = result.scalar()
        print(f"✅Connected! Found {count} addressess")


        # check if embedding columns exists

        result = conn.execute(text("""
                SELECT column_name 
                from information_schema.columns
                WHERE table_name = 'address_registry'
                and column_name = 'embedding'
        """))

        if result.fetchone():
            print("✅ Embedding column exists")
        else:
            print("❌ Embedding column missing")

if __name__ == "__main__":
    test_connection()