# openapi.py

from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field

class Item(BaseModel):
    brand: str = Field(..., example="Yamaha")
    model_type: str = Field(..., example="YZF-R1")
    model_frameworks: str = Field(..., example="independent_model")
    brand_new_date: str = Field(..., example="2023-06-15T00:00:00.000Z")
    repossessed_date: str = Field(..., example="2024-01-10T00:00:00.000Z")

def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Armas Motorcycle Evaluation API",
        version="1.0.0",
        description="This FastAPI app serves as a backend for a motorcycle evaluation system. It receives motorcycle details, images, and audio recordings, and provides a prediction on the motorcycle's status using ensemble modeling techniques.",
        routes=app.routes,
    )

    # Modify the "paths" to delete unwanted response codes
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if method.get("responses"):
                method["responses"].pop("200", None)
                method["responses"].pop("422", None)

    return openapi_schema
