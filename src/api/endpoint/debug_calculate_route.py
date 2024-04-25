# debug_calculate_route.py

import io
import logging
import shutil
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, APIRouter
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assume other necessary modules and functions are imported and defined here...

router = APIRouter()

@router.post("/calculate")
async def calculate_button(
    Brand: str = Form(...),
    ModelType: str = Form(...),
    ModelFrameworks: str = Form(...),
    GetDate: str = Form(...),
    ReturnDate: str = Form(...),
    LeftImageFile: UploadFile = File(...),
    RightImageFile: UploadFile = File(...),
    FrontImageFile: UploadFile = File(...),
    RearImageFile: UploadFile = File(...),
    AudioFile: UploadFile = File(...)
):
    try:
        # Debug: Print the received form data
        logging.info(f"Received Brand: {Brand}")
        logging.info(f"Received ModelType: {ModelType}")
        logging.info(f"Received ModelFrameworks: {ModelFrameworks}")
        logging.info(f"Received GetDate: {GetDate}")
        logging.info(f"Received ReturnDate: {ReturnDate}")

        # Debug: Print file information
        logging.info(f"Received LeftImageFile: {LeftImageFile.filename}")
        logging.info(f"Received RightImageFile: {RightImageFile.filename}")
        logging.info(f"Received FrontImageFile: {FrontImageFile.filename}")
        logging.info(f"Received RearImageFile: {RearImageFile.filename}")
        logging.info(f"Received AudioFile: {AudioFile.filename}")

        # Further processing here...
        # ...

        # Return a mock response for now
        return {"ensemble_prediction": "mock_prediction"}

    except ValueError as e:
        logger.error(f"Validation error: {str(e)} - Get Date: {GetDate}, Return Date: {ReturnDate}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Clean up the temporary files if necessary
        await cleanup_temp_files(LeftImageFile, RightImageFile, FrontImageFile, RearImageFile, AudioFile)

async def cleanup_temp_files(*files):
    for file in files:
        if file.file:
            file.file.close()
            if os.path.exists(file.filename):
                os.remove(file.filename)
                logging.info(f"Cleaned up file: {file.filename}")
