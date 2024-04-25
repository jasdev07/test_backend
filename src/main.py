# src/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from .api.endpoint.calculate_route import router as calculate_router
from .api.endpoint.general_routes import router as general_router
from .core.openapi import custom_openapi

app = FastAPI()

# Load environment variables
load_dotenv()

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(calculate_router)
app.include_router(general_router)

# Modify the OpenAPI schema
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return custom_openapi(app)

# Adjust FastAPI app's openapi method to use custom_openapi
app.openapi = lambda: custom_openapi(app)
