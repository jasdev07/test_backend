
# src/api/endpoint/general_routes.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
	"""
	Health check endpoint for the application. This endpoint will be used by the
	Docker container to check the application's health status. A response indicating
	the application is 'healthy' signifies that the application is running and can
	respond to HTTP GET requests. If the endpoint is unreachable or the application
	is not running correctly, the health check will fail.
	"""
	return {"status": "healthy"}