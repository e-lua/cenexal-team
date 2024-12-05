# Use an official Python runtime as a parent image
FROM python:3.11.4

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies and ODBC requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    unixodbc \
    unixodbc-dev \
    gnupg2 \
    curl \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install uvicorn fastapi python-multipart openpyxl

# Copy the current directory contents into the container
COPY . /app

# Command to run on container start
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]