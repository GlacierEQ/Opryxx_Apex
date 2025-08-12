"""
OPRYXX ASGI Application Entry Point
FastAPI wrapper for OPRYXX system components
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ENHANCED_PIPELINES import EnhancedPipelineProcessor
from INTEGRATION_BRIDGE import setup_opryxx_integration

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.pipeline = EnhancedPipelineProcessor()
    app.state.integration = setup_opryxx_integration()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="OPRYXX System API",
    description="Ultimate System Integration API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "opryxx-api"}

@app.post("/execute")
async def execute_command(query: str):
    try:
        command_info = app.state.pipeline.parse_natural_language(query)
        result = await app.state.pipeline.execute_command(command_info)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operations")
async def get_operations():
    return app.state.pipeline.get_all_operations()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)