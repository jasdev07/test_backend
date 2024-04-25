# src/preprocessing/audio_utils.py
from subprocess import run, PIPE

def convert_audio_to_wav(input_file_path: str, output_file_path: str):
	"""
	Converts an audio file to WAV format using ffmpeg.

	Args:
		input_file_path (str): The file path of the input audio file.
		output_file_path (str): The file path where the converted WAV file will be saved.

	Raises:
		Exception: If ffmpeg encounters an error during the conversion process.
	"""
	# Construct the ffmpeg command for converting the audio file
	command = ["ffmpeg", "-i", input_file_path, output_file_path]
	# Execute the ffmpeg command
	result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
	
	# Check if the command was successful (returncode 0 indicates success)
	if result.returncode != 0:

		# If an error occurred (non-zero returncode), raise an exception with the error message
		raise Exception(f"ffmpeg error: {result.stderr}")

