from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import disease, websocket

app = FastAPI(
    title="EpiScope API",
    description="API for disease monitoring and prediction",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(disease.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to EpiScope API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "websocket_url": "/ws/monitor/{client_type}"
    } 