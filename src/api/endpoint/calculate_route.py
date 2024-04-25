import io
import logging
import librosa
import shutil
import numpy as np
import os
import pickle
import tensorflow as tf


from PIL import Image
from datetime import datetime
from autogluon.tabular import TabularPredictor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, APIRouter
from typing import List
from pathlib import Path
from src.preprocessing.preprocessing_pipeline_e1 import classes
from src.preprocessing.preprocessing_pipeline_e1 import test01
from src.utils.audio_utils import convert_audio_to_wav
from utils.model_loader import ALPHA, BETA, test01

router = APIRouter()
# Set up logging
logger = logging.getLogger(__name__)

# Correct the DATA_DIR to reflect the path from the src directory
DATA_DIR = Path(__file__).parents[2] / 'path of preprocessing' / 'The file '

image_model, audio_model, tabular_model = load_models()

# This code is upon for calucating button
@router.post("/calculate")
async def calculate_button(
		Brand: str = Form(
			..., 
			description="Brand of the motorcycle.\n\n"
						"    Example: 'Yamaha'"
		),
		ModelType: str = Form(
			..., 
			description="Model Type of the motorcycle.\n\n"
						"    Example: 'YZF-R1'"
		),
		ModelFrameworks: str = Form(
			..., 
			description="Framework of the motorcycle.\n\n"
						"    Example: 'independent_model'"
		),
		GetDate: str = Form(
			..., 
			description="The manufacturing date of the motorcycle.\n\n"
						"    Example: '2023-06-15T00:00:00.000Z'"
		),
		ReturnDate: str = Form(
			..., 
			description="The date when the motorcycle was repossessed.\n\n"
						"    Example: '2024-01-10T00:00:00.000Z'"
		),
		LeftImageFile: UploadFile = File(
			..., 
			description="Upload the left side image of the motorcycle.\n\n"
						"    Note: The image should clearly show the left side."
		),
		RightImageFile: UploadFile = File(
			..., 
			description="Upload the right side image of the motorcycle.\n\n"
						"    Note: The image should clearly show the right side."
		),
		FrontImageFile: UploadFile = File(
			..., 
			description="Upload the front image of the motorcycle.\n\n"
						"    Note: The image should clearly show the front view."
		),
		RearImageFile: UploadFile = File(
			..., 
			description="Upload the rear image of the motorcycle.\n\n"
						"    Note: The image should clearly show the rear view."
		),
		AudioFile: UploadFile = File(
			..., 
			description="Upload an audio file containing the sound of the motorcycle's engine.\n\n"
						"    Note: The audio should be clear and without background noise."
		)

	):

	try:
		# Temporary file paths
		temp_audio_m4a = 'temp_audio.m4a'
		temp_audio_wav = 'temp_audio.wav'

		# Parsing dates from string to datetime
		brand_new_date = datetime.strptime(GetDate, "%Y-%m-%dT%H:%M:%S.%fZ")
		repossessed_date = datetime.strptime(ReturnDate, "%Y-%m-%dT%H:%M:%S.%fZ")

		# Read image bytes
		left_image_bytes = await LeftImageFile.read()
		front_image_bytes = await FrontImageFile.read()
		right_image_bytes = await RightImageFile.read()
		rear_image_bytes = await RearImageFile.read()


		# Open images from the uploaded files
		left_image = Image.open(io.BytesIO(left_image_bytes))
		front_image = Image.open(io.BytesIO(front_image_bytes))
		right_image = Image.open(io.BytesIO(right_image_bytes))
		rear_image = Image.open(io.BytesIO(rear_image_bytes))


		# image library processing
		cur_images = {
			'front': front_image,
			'rear': rear_image,
			'right': right_image,
			'left': left_image
		}
		
		########## Audio model processing ###########
		# Save the uploaded audio file temporarily and process
		with open(temp_audio_m4a, 'wb') as temp_file:
			shutil.copyfileobj(AudioFile.file, temp_file)

		# Attempt to process the audio file with librosa
		try:
			audio_ts, sr = librosa.load(temp_audio_m4a, sr=None, duration=9, mono=True)
		except Exception as librosa_error:
			# If librosa fails, convert the file to WAV and retry
			print(f"Librosa failed to load the audio file: {librosa_error}, converting to WAV.")
			# This matches the function definition now
			convert_audio_to_wav(temp_audio_m4a, temp_audio_wav)  
			audio_ts, sr = librosa.load(temp_audio_wav, sr=None, duration=9, mono=True)
			# Clean up the converted WAV file after processing
			os.remove(temp_audio_wav)

		if ModelFrameworks == 'independent_model':

			######## Imagee model processing ##########

			cur_sample = prepare_sample_from_images(cur_images)
			image_prediction = get_prediction(cur_sample, image_model)

			######### Tabular model processing #########
			tabular_sample = preprocess_tabular(brand_new_date, repossessed_date, ModelType)
			tabular_prediction = classes[tabular_model.predict(tabular_sample).iloc[0]]

			# Preprocess the audio data for the model
			audio_sample = preprocess_audio(audio_ts, sr)

			# Predict using the audio model and get the first result
			audio_class = audio_model.predict(audio_sample).iloc[0]

			# Convert the prediction to a more interpretable form using the 'classes' dictionary
			audio_prediction = classes[audio_class]

			########## Ensemble ###########
			ensemble_prediction = get_ensemble_predictions(ALPHA, BETA, image_prediction, audio_prediction, tabular_prediction)

			print("Ensemble Prediction", ensemble_prediction)
			# Return the prediction result
			return {"ensemble_prediction": ensemble_prediction}
		
		elif ModelFrameworks == 'deep_network':
			print('ModelFrameworks is deep_network')

			# Open the file in binary read mode
			with DATA_DIR.open('rb') as file:
				tab_columns = pickle.load(file)


			# Prepare data for ensemble framework 2
			data_input = create_torch_records(cur_images,
											  audio_ts, sr,
											  tab_columns,
											  brand_new_date,
											  repossessed_date,
											  ModelType)
			# print (data_input,tab_columns, 'yeheyyyyyyyyyyyyyyyyyyyyy' )

			model_filepath = 'path of the model'
			ensemble_prediction = predict_class(model_filepath, data_input)
		
			print("Ensemble Prediction", ensemble_prediction)
			# Return the prediction result
			return {"ensemble_prediction": ensemble_prediction}

	except ValueError as e:
		logger.error(f"Validation error: {str(e)} - Get Date: {GetDate}, Return Date: {ReturnDate}")
		raise HTTPException(status_code=400, detail=str(e))
	finally:
		# Clean up the temporary M4A file
		if os.path.exists(temp_audio_m4a):
			os.remove(temp_audio_m4a)
