# Use an official, lightweight Python runtime as a parent image
FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Set system environment variables to optimize Python inside the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements first to leverage Docker caching layers
COPY requirements.txt .

# Install dependencies cleanly without saving cache files to minimize image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application source code into the container
COPY main.py parser.py ./

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the Uvicorn ASGI server on container boot
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]