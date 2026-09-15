FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System dependencies for PDF/OCR (optional for local OCR)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       poppler-utils \
       tesseract-ocr \
       libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY app.py ./

ENV PYTHONPATH=/app/src
ENV STREAMLIT_SERVER_HEADLESS=true
EXPOSE 8080

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
