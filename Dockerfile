FROM python:3.10.12-slim
ARG group

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Creating a new user, upgrading pip to the latesr version and installing poetry
RUN useradd -ms /bin/bash newuser && \
    python -m pip install --upgrade pip && \
    pip install poetry

# Copy pyproject.toml and poetry.lock to install dependencies
WORKDIR /project
COPY pyproject.toml poetry.lock ./

# Installing dependencies to system python
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction $group

# Сopy the remaining files
COPY . .

# Runing the file as an executable script
RUN chmod +x scripts/entrypoint_webapp.sh

# Changing user 
USER newuser

# Launching the script
ENTRYPOINT [ "scripts/entrypoint_webapp.sh" ]

# Checking health status
HEALTHCHECK --interval=3s --timeout=10s --start-period=15s --retries=5 \
  CMD curl -f $WEBAPP_HOST/healthcheck || exit 1
