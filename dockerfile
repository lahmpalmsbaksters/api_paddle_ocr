# Use a base image with Python (adjust the version as needed)
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy your FastAPI application code into the container
COPY app /app

# Install any required Python packages
RUN pip install fastapi paddlepaddle paddleocr uvicorn
RUN pip install -r /app/requirements.txt

# Expose the port your FastAPI application will run on (default is 8000)
EXPOSE 8000

# Command to start your FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
