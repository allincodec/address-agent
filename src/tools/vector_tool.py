import sys
from pathlib import Path

# Add parent directory to path so we can import from database package
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sentence_transformers import SentenceTransformer
from database.connection import engine


class VectorSearchTool:

    def __init__(self):
        print("Loading embedding model")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded")

    def search(self, query: str, limit: int = 5) -> str:
        """Search addresses using semantic similarity"""

        query_embedding = self.model.encode(query)
        print(f"Query: {query}")
        print(f"Embedding generated: {len(query_embedding)} dimensions")

        with engine.connect() as conn:
            check = conn.execute(text("""
                SELECT COUNT(*) as total
                FROM address_registry
                WHERE embedding IS NOT NULL
            """))
            count = check.scalar()
            print(f"✅ Addresses with embeddings: {count}")

            if count == 0:
                return "No embeddings found in database. Run embedding_generator.py first!"

            # Use f-string to build vector literal
            vector_str = str(query_embedding.tolist())

            result = conn.execute(text(f"""
                SELECT
                    name,
                    city,
                    country_name,
                    address_line_1,
                    location_id,
                    state,
                    address_type,
                    embedding <-> '{vector_str}'::vector(384) as distance
                FROM address_registry
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> '{vector_str}'::vector(384)
                LIMIT {limit}
            """))

            matches = result.fetchall()
            print(f"Matches found: {len(matches)}")

            if not matches:
                return "No results found"

            output = f"Found {len(matches)} similar addresses:\n"
            for i, match in enumerate(matches, 1):
                output += f"{i}. {match.location_id} - {match.city}, {match.country_name}, {match.state} ({match.address_type}) [distance: {match.distance:.3f}]\n"

            return output


if __name__ == "__main__":
    tool = VectorSearchTool()
    print(tool.search("Berthier-sur-Mer canada", limit=3))
    print("\n")
    print(tool.search("norway terminal", limit=3))
    print("\n")
    print(tool.search("port korea", limit=3))
    print("\n")
    print(tool.search("address with location id NOETN", limit=3))
    print("\n")
    print(tool.search("address with country name as ukraine", limit=3))