# Use a base image with Python (adjust the version as needed)
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy your FastAPI application code into the container
COPY . /app

# Install any required Python packages
RUN apt-get update && apt-get install -y curl
RUN curl -O http://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb
RUN pip install --upgrade pip
RUN pip install firebase-admin
RUN pip install --upgrade urllib3
RUN pip install python-multipart
RUN pip install uuid7
RUN pip install fastapi paddlepaddle paddleocr uvicorn
RUN pip install -r /app/requirements.txt
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6
RUN dpkg -i libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb

# Command to start your FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]

