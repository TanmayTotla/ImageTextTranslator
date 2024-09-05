# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install Tesseract and any other dependencies
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run gunicorn to start your app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
