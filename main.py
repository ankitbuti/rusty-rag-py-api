from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime
import uuid

import weaviate
from weaviate.classes.init import Auth

# Data Models
class Record(BaseModel):
    id: Optional[str] = None

    title: str
    content: str
    repo_url: str
    package_url: str
    description: str
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RecordCreate(BaseModel):
    title: str
    content: str
    repo_url: Optional[str] = ""
    package_url: Optional[str] = ""
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

class RecordResponse(BaseModel):
    name: str
    description: str
    readme: str
    crates_url: str
    repo_url: str

class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 10
    tags: Optional[List[str]] = None

class SearchResponse(BaseModel):
    results: List[RecordResponse]
    total: int
    query: str

# In-memory storage (replace with database in production)
records_storage: Dict[str, Record] = {}

# Create FastAPI instance
app = FastAPI(
    title="Rusty-RAG API",
    description="AI Search API for Developer Packages with CRUD operations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_weaviate_client():
    """Get Weaviate client connection"""
    try:
        # Best practice: store your credentials in environment variables
        weaviate_url = os.environ.get("WEAVIATE_URL")
        weaviate_api_key = os.environ.get("WEAVIATE_API_KEY")

        if not weaviate_url or not weaviate_api_key:
            raise HTTPException(
                status_code=500,
                detail="Weaviate configuration missing. Please set WEAVIATE_URL and WEAVIATE_API_KEY environment variables."
            )

        # Connect to Weaviate Cloud
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=Auth.api_key(weaviate_api_key),
        )

        if not client.is_ready():
            raise HTTPException(status_code=500, detail="Weaviate client is not ready")

        return client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Weaviate: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint that returns a hello world message"""
    return {"message": "Hello! from Rusty-RAG API. AI Search for ANY Developer Package."}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "hello-world-api"}

@app.get("/hello/{name}")
async def hello_name(name: str):
    """Personalized hello endpoint"""
    return {"message": f"Hello {name}! Welcome to our FastAPI service"}

# CRUD Operations

@app.post("/records", response_model=RecordResponse)
async def create_record(record: RecordCreate):
    """Insert a single record"""
    try:
        # Generate unique ID and timestamps
        record_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Create new record
        new_record = Record(
            id=record_id,
            title=record.title,
            content=record.content,
            repo_url=record.repo_url or "",
            package_url=record.package_url or "",
            description=record.description or "",
            tags=record.tags or [],
            metadata=record.metadata or {},
            created_at=now,
            updated_at=now
        )

        # Store in memory
        records_storage[record_id] = new_record

        return RecordResponse(
            id=new_record.id,
            title=new_record.title,
            content=new_record.content,
            repo_url=new_record.repo_url,
            package_url=new_record.package_url,
            description=new_record.description,
            tags=new_record.tags,
            metadata=new_record.metadata,
            created_at=new_record.created_at,
            updated_at=new_record.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")

@app.post("/records/batch", response_model=List[RecordResponse])
async def create_multiple_records(records: List[RecordCreate]):
    """Insert multiple records"""
    try:
        if len(records) > 100:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size cannot exceed 100 records")

        created_records = []
        now = datetime.utcnow()

        for record in records:
            # Generate unique ID
            record_id = str(uuid.uuid4())

            # Create new record
            new_record = Record(
                id=record_id,
                title=record.title,
                content=record.content,
                repo_url=record.repo_url or "",
                package_url=record.package_url or "",
                description=record.description or "",
                tags=record.tags or [],
                metadata=record.metadata or {},
                created_at=now,
                updated_at=now
            )

            # Store in memory
            records_storage[record_id] = new_record

            created_records.append(RecordResponse(
                id=new_record.id,
                title=new_record.title,
                content=new_record.content,
                repo_url=new_record.repo_url,
                package_url=new_record.package_url,
                description=new_record.description,
                tags=new_record.tags,
                metadata=new_record.metadata,
                created_at=new_record.created_at,
                updated_at=new_record.updated_at
            ))

        return created_records
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating records: {str(e)}")

@app.get("/search", response_model=SearchResponse)
async def search_records(query: str, limit: int | None = None):
    """Search records by query and optional tags"""
    client = await get_weaviate_client()
    try:
        crates = client.collections.get(name="crates")
        response = crates.query.near_text(
            query=query,
            limit=limit,
        )

        records = []
        for crate in response.objects:
            records.append(RecordResponse(
                name=crate.properties['name'],
                description=crate.properties['description'],
                readme=crate.properties['readme'],
                crates_url=f"https://crates.io/crates/{crate.properties['name']}",
                repo_url=crate.properties['repository'],
            ))
        return SearchResponse(
            results=records,
            total=len(records),
            query=query,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        client.close()

@app.get("/records", response_model=List[RecordResponse])
async def get_all_records(limit: int = 50, offset: int = 0):
    """Get all records with pagination"""
    try:
        all_records = list(records_storage.values())
        all_records.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        start = offset
        end = offset + limit
        paginated_records = all_records[start:end]

        return [
            RecordResponse(
                id=record.id,
                title=record.title,
                content=record.content,
                repo_url=record.repo_url,
                package_url=record.package_url,
                description=record.description,
                tags=record.tags,
                metadata=record.metadata,
                created_at=record.created_at,
                updated_at=record.updated_at
            )
            for record in paginated_records
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving records: {str(e)}")

@app.get("/records/{record_id}", response_model=RecordResponse)
async def get_record(record_id: str):
    """Get a specific record by ID"""
    if record_id not in records_storage:
        raise HTTPException(status_code=404, detail="Record not found")

    record = records_storage[record_id]
    return RecordResponse(
        id=record.id,
        title=record.title,
        content=record.content,
        repo_url=record.repo_url,
        package_url=record.package_url,
        description=record.description,
        tags=record.tags,
        metadata=record.metadata,
        created_at=record.created_at,
        updated_at=record.updated_at
    )

# For local development only
if __name__ == "__main__":
    # Get port from environment variable (required for Cloud Run)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
