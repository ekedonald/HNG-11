FROM python:3.10-slim

USER root

WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y curl wait-for-it

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set environment variables for Poetry
ENV PATH="/root/.local/bin:$PATH"
ENV DB_HOST=database
ENV DB_PORT=5432

# Copy only the necessary files first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install project dependencies
RUN poetry install

# Copy the rest of the application files
COPY . /app

ENV PYTHONPATH=/app

# Copy the prestart script
COPY prestart.sh /app/prestart.sh
RUN chmod +x /app/prestart.sh

# Command to run the application
CMD cd /app && \
    wait-for-it ${DB_HOST}:${DB_PORT} -- poetry run bash ./prestart.sh && \
    poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000