FROM python:3.12-slim

# Set the working directory
WORKDIR /LUCKYDEPOT

# Copy the application folder
COPY . .

# Set the working directory for the app
# WORKDIR /LUCKYDEPOT/fastapi

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ENV DATESPOT_DB=""
# ENV DATESPOT_DB_USER=""
# ENV DATESPOT_DB_PASSWORD=""
# ENV DATESPOT_DB_TABLE=""
# ENV DATESPOT_PORT=""
# ENV REDIS_HOST=""
# ENV REDIS_PORT=""
# ENV REDIS_PASSWORD=""

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
