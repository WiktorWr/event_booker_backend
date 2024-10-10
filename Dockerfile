FROM python:3.12-slim
WORKDIR /code
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false
RUN poetry install
COPY . .