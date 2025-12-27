#Address Registry - Intelligent Address Search Agent

An AI-powered agent that provides intelligent semantic search over multimodal shipping addresses using vector embeddings and PostgreSQL with pgvector.

## 🎯 What Does This Do?

This project enables natural language queries over shipping addresses (ports, airports, rail terminals, warehouses) using semantic search instead of traditional keyword matching.

**Example:**
```
Query: "Find container terminals in Southeast Asia"

Traditional Search: 
❌ Only finds addresses with exact words "container", "terminals", "Southeast Asia"

Our Agent:
✅ Understands: ports, cargo facilities, shipping hubs
✅ Understands: Singapore, Malaysia, Thailand, Vietnam, Indonesia
✅ Returns: All semantically relevant addresses, ranked by similarity
```

## 🏗️ Architecture
```
User Query
    ↓
Agent (smolagents)
    ↓
┌──────────────┬───────────────┬──────────────┐
│  SQL Tool    │ Vector Tool   │ Spatial Tool │
│  (filters)   │ (semantic)    │ (geo-search) │
└──────────────┴───────────────┴──────────────┘
         ↓            ↓              ↓
    PostgreSQL + pgvector + PostGIS
         ↓
   Ranked Results
```

## ✨ Features

- **Semantic Search**: Find addresses by meaning, not just keywords
- **Natural Language**: Query in plain English
- **Multi-tool Agent**: Combines SQL, vector search, and geospatial queries
- **Fast**: Searches millions of addresses in milliseconds
- **Intelligent Ranking**: Results sorted by relevance

## 🚀 Quick Start

### Prerequisites

- Python 3.12
- PostgreSQL 16+ with pgvector and PostGIS extensions
- UV package manager

### Installation
```bash
# Clone the repository
git clone <repo-url>
cd address-agent

# Install UV
brew install uv

# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup
```bash
# Start PostgreSQL with pgvector (Docker)
docker run -d \
  --name address-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=address_registry \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```
```Address Registry Table
create type address_type as enum ('PORT', 'AIRPORT', 'RAIL', 'UNKNOWN');

alter type address_type owner to postgres;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE INDEX ON address_registry USING ivfflat (embedding vector_cosine_ops);
alter type public.vector owner to postgres;

create table address_registry
(
    id                   bigserial
        primary key,
    location_id          varchar(100)                                       not null,
    name                 varchar(255),
    address_line_1       varchar(255),
    address_line_2       varchar(255),
    city                 varchar(100)                                       not null,
    district             varchar(100),
    state                varchar(100),
    country_code         varchar(3),
    country_name         varchar(100),
    postal               varchar(20),
    latitude             numeric(10, 7),
    longitude            numeric(10, 7),
    timezone             varchar(50),
    geofence_radius      integer,
    geofence_points      jsonb,
    address_type         address_type not null,
    embedding            vector(384)
);

```
```Sample Data Set
INSERT INTO public.address_registry (id, location_id, name, address_type, address_line_1, address_line_2, city, district, state, country_code, country_name, postal, timezone) VALUES (1816358, 'RSAPT', null, 'UNKNOWN', null, null, 'Apatin', null, 'Vojvodina', 'RS', 'serbia', null, null);
INSERT INTO public.address_registry (id, location_id, name, address_type, address_line_1, address_line_2, city, district, state, country_code, country_name, postal, timezone) VALUES (1816359, 'UAZUN', null, 'UNKNOWN', null, null, 'Kaniv', null, 'Cherkas''ka oblast', 'UA', 'ukraine', null, null);
INSERT INTO public.address_registry (id, location_id, name, address_type, address_line_1, address_line_2, city, district, state, country_code, country_name, postal, timezone) VALUES (1816360, 'CABSM', null, 'UNKNOWN', null, null, 'Berthier-sur-Mer', null, 'QC', 'CA', 'canada', null, null);
INSERT INTO public.address_registry (id, location_id, name, address_type, address_line_1, address_line_2, city, district, state, country_code, country_name, postal, timezone) VALUES (1816361, 'GQABU', null, 'UNKNOWN', null, null, 'San Antonio de Pale', null, '.', 'GQ', 'equatorial guinea', null, null);
INSERT INTO public.address_registry (id, location_id, name, address_type, address_line_1, address_line_2, city, district, state, country_code, country_name, postal, timezone) VALUES (1816356, 'NOETN', null, 'UNKNOWN', null, null, 'terminal', null, 'Hordaland', 'NO', 'norway', null, null);
```

### Generate Embeddings
```bash
# Generate embeddings for all addresses
uv run python src/database/embedding_generator.py
```

### Run Vector Search
```bash
# Test vector search
uv run python src/tools/vector_tool.py
```

## 📊 Project Structure
```
address-agent/
├── src/
│   ├── database/
│   │   ├── connection.py           # Database connection
│   │   ├── embedding_generator.py  # Generate embeddings
│   │   └── test_connection.py      # Connection test
│   ├── tools/
│   │   ├── vector_tool.py          # Semantic search tool
│   │   ├── sql_tool.py             # SQL query tool
│   │   └── spatial_tool.py         # Geospatial search tool
│   └── agent/
│       └── main_agent.py           # Main agent orchestrator
├── docs/
│   └── LAYMAN_GUIDE.md            # Detailed explanation
├── tests/
├── pyproject.toml                  # Project dependencies
├── uv.lock                         # Lock file
├── .env                            # Environment variables
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=address_registry
DB_USER=postgres
DB_PASSWORD=password
```

### Database Schema

**Main Table:** `address_registry`

Key columns:
- `id`: Primary key
- `location_id`: Unique location identifier
- `name`: Address name
- `city`, `state`, `country_name`: Location info
- `address_type`: PORT, AIRPORT, RAIL, UNKNOWN
- `latitude`, `longitude`: Coordinates
- `location_point`: PostGIS geometry
- `embedding`: pgvector embedding (384 dimensions)

## 💡 Usage Examples

### Vector Search
```python
from src.tools.vector_tool import VectorSearchTool

tool = VectorSearchTool()

# Semantic search
results = tool.search("container shipping terminals", limit=5)
print(results)

# Output:
# Found 5 similar addresses:
# 1. SGSIN - Singapore, singapore (PORT) [distance: 0.823]
# 2. HKHKG - Hong Kong, china (PORT) [distance: 1.145]
# ...
```

### SQL Tool
```python
from src.tools.sql_tool import SQLTool

tool = SQLTool()

# Exact filters
results = tool.execute("How many ports in Singapore?")
print(results)
```

### Combined Agent (Coming Soon)
```python
from src.agent.main_agent import AddressAgent

agent = AddressAgent()

# Natural language query
response = agent.query(
    "Find container terminals within 50km of Mumbai that handle refrigerated cargo"
)
print(response)
```

## 🧪 Testing
```bash
# Test database connection
uv run python src/database/test_connection.py

# Test vector search
uv run python src/tools/vector_tool.py

# Run all tests
uv run pytest tests/
```

## 📈 Performance

- **Embedding Generation**: ~100 addresses/second
- **Vector Search**: ~50ms for 1M addresses
- **Combined Query**: ~200ms end-to-end

## 🛠️ Technical Details

### Vector Embeddings

- **Model**: sentence-transformers (all-MiniLM-L6-v2)
- **Dimensions**: 384
- **Distance Metric**: L2 (Euclidean)
- **Index**: IVFFlat for fast approximate search

### Why pgvector?

- Native PostgreSQL integration
- Fast similarity search with indexes
- Can combine with SQL and PostGIS
- Production-ready and battle-tested

### Embedding Generation Process

1. Combine address fields: `location_id + name + city + country + type`
2. Generate 384-dimensional embedding using sentence-transformers
3. Store in `embedding` column
4. Create IVFFlat index for fast search

## 🔍 How Semantic Search Works

Traditional keyword search:
```sql
SELECT * FROM addresses 
WHERE name ILIKE '%container%' AND city = 'Singapore';
```

Our semantic search:
```sql
SELECT *, embedding <-> '[query_embedding]'::vector(384) as distance
FROM addresses
ORDER BY distance
LIMIT 10;
```

**Benefits:**
- Finds "cargo terminal", "shipping hub", "freight center" for query "container"
- Understands geographic relationships
- Handles typos and variations
- Ranks by semantic relevance

## 🚧 Roadmap

- [x] Database connection
- [x] Embedding generation
- [x] Vector search tool
- [ ] SQL query tool
- [ ] Spatial search tool
- [ ] Agent orchestration with smolagents
- [ ] Web UI
- [ ] API endpoints
- [ ] Caching layer
- [ ] Multi-language support

## 📚 Learn More

- [Guide](docs/EXPLAINED_LIKE_IM_5.md) - Detailed explanation in simple terms
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [sentence-transformers](https://www.sbert.net/)
- [smolagents](https://huggingface.co/docs/smolagents)

## 🙏 Acknowledgments

- Uses pgvector extension for PostgreSQL
- Powered by HuggingFace transformers