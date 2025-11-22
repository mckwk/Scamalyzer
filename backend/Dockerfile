# Use official Python image
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy backend code
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]