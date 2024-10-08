FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y tesseract-ocr

RUN pip install gunicorn

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

#Uses gunicorn to start the flask application and bind it to port 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
