# Use a lightweight official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency files first (for better layer caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN chgrp -R 0 /app && chmod -R g=u /app

USER 1001

# Expose the Flask app port
EXPOSE 5000

# Set environment variables (can be overridden at runtime)
ENV FLASK_APP=maximoagents.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the application
CMD ["python", "maximoagents.py"]
