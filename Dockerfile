# Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]


# docker login -u "owenmurphy2022v1" -p "Dotdu2-qukvih-hyhgid" docker.io