# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# The command to run the application will be specified in the docker-compose.yml
# But we can add a default command here for completeness
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]