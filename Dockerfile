FROM python:3.12.2-slim
ARG group

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -ms /bin/bash newuser && \
    python -m pip install --upgrade pip && \
    pip install poetry

WORKDIR /project
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction $group

COPY . .

RUN chown -R newuser:newuser . && \
    chmod +x scripts/entrypoint_webapp.sh

USER newuser

ENTRYPOINT [ "scripts/entrypoint_webapp.sh" ]
