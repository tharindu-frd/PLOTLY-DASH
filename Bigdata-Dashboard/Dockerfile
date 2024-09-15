FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4819

ENV NAME World

CMD ["python", "dashboard.py"]
