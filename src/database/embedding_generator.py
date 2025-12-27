from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from connection import engine  # Changed from src.database.connection


class EmbeddingGenerator:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✅ Model loaded!")

    def create_address_text(self, address):
        """Combine address fields into searchable text"""
        parts = [
            address.get('location_id', ''),
            address.get('name', ''),
            address.get('address_type', ''),
            address.get('address_line_1', ''),
            address.get('address_line_2', ''),
            address.get('city', ''),
            address.get('district', ''),
            address.get('state', ''),
            address.get('country_code', ''),
            address.get('country_name', ''),
            address.get('postal', ''),
            address.get('timezone', '')
        ]
        return ' '.join([str(p) for p in parts if p]).strip()

    def generate_embedding(self, text):
        """Generate embedding for text"""
        return self.model.encode(text)

    def generate_embeddings_batch(self, limit=10):
        """Generate embeddings for addresses without them"""
        with engine.connect() as conn:
            # Get addresses without embeddings
            result = conn.execute(text(f"""
                SELECT id, location_id, name, address_type, address_line_1, address_line_2, 
                       city, district, state, country_code, country_name, postal, timezone
                FROM address_registry
                WHERE embedding IS NULL
                LIMIT {limit}     
            """))

            addresses = result.fetchall()
            print(f"Found {len(addresses)} addresses to embed")

            for addr in addresses:
                # Create text representation
                addr_dict = dict(addr._mapping)
                addr_text = self.create_address_text(addr_dict)
                print(f"Processing: {addr_text[:50]}...")

                # Generate embedding
                embedding = self.generate_embedding(addr_text)

                # Store in database
                conn.execute(text("""
                    UPDATE address_registry 
                    SET embedding = :embedding 
                    WHERE id = :id
                """), {"embedding": embedding.tolist(), "id": addr_dict['id']})

            conn.commit()
            print(f"✅ Generated {len(addresses)} embeddings")


if __name__ == "__main__":
    generator = EmbeddingGenerator()
    generator.generate_embeddings_batch(limit=5)