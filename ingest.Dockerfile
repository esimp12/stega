FROM python:latest AS poetry-base

RUN curl -sSL https://install.python-poetry.org | python3 - --preview

ENV PATH="/root/.local/bin:$PATH"

FROM poetry-base AS stega-ingest

WORKDIR /usr/src/stega

COPY poetry.lock pyproject.toml README.md /usr/src/stega/

COPY config /usr/src/stega/config

COPY src /usr/src/stega/src

RUN poetry config virtualenvs.create false \
  && poetry install --no-cache --only main --no-interaction --no-ansi

CMD ["poetry", "run", "ingest"]
