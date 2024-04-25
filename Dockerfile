# Use a base image with Miniconda installed
FROM continuumio/miniconda3:4.9.2

# Set the working directory in the container
WORKDIR /app

# Copy the environment.yml file
COPY environment.yml /app/environment.yml

# Create the Conda environment
RUN conda env create -f /app/environment.yml 

# Make sure the environment is activated:
ENV PATH /opt/conda/envs/armas/bin:$PATH

# Install the requirements using pip (if any)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the content of the src directory to the container
COPY ./src /app/src

# Copy the preprocessing directory into the image
COPY ./src/preprocessing /app/preprocessing

# At the end, before CMD, add the following line to set PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Command to run the application, using bash to ensure environment activation
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8082"]
