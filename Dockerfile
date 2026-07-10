FROM python:3.14-slim

RUN apt update && apt install -y --no-install-recommends curl

RUN pip install --no-cache-dir poetry

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false

COPY poetry.lock pyproject.toml ./

# RUN poetry install --only main --no-root
RUN poetry install

COPY . /app

CMD ["python", "src/app.py"]
