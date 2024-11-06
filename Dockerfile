# Use an official Python runtime as a parent image
FROM python:3.11.4

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install uvicorn

RUN pip install fastapi

RUN pip install python-multipart

RUN pip install openpyxl

# Copy the current directory contents into the container
COPY . /app

# Command to run on container start
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]