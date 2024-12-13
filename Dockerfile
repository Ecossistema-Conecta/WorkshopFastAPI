FROM python:3.12-bullseye

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
