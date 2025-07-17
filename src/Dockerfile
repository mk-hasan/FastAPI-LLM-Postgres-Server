# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /src

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy Poetry files and install Poetry
COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir poetry

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]