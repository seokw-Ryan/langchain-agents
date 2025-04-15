FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Don't copy the source code - it will be mounted as a volume
# COPY . .

EXPOSE 8000

# Use --reload flag for development to auto-reload when files change
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 