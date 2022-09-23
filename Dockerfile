FROM python:3.10-slim-buster AS poetry
RUN pip install poetry
# Get Rust

WORKDIR /coingecko_redis
COPY pyproject.toml poetry.lock .
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
FROM python:3.10-slim
RUN apt-get update
WORKDIR /coingecko_redis
COPY --from=poetry /coingecko_redis/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH .

CMD ["python","./coingecko_redis/main.py"]
