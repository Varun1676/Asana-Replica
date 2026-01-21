# FROM python:3.11-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install sqlmodel datamodel-code-generator uvicorn[standard] python-multipart aiohttp

# COPY . .

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# OLD: FROM python:3.11-slim
# NEW: Use Amazon's mirror to bypass Docker Hub auth
FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]