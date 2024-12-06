FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    apt-get install -y libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY credentials.env /app/credentials.env
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /app/myvol

EXPOSE 5000
CMD ["python", "app.py"]
