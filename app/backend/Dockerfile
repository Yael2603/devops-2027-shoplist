FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY wheels/ /wheels/

RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
