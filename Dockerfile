FROM python:3.11

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV REDIS_HOST="redis"

RUN pip install poetry

# Set working directory
WORKDIR /app

# Install project dependencies
COPY pyproject.toml poetry.lock /app/

# Copy the notebooks from getting_started
# COPY getting_started /app/getting_started
COPY python-examples/auto_test /app/auto_test


RUN poetry config virtualenvs.create false && poetry install --all-extras

# Run tests
CMD ["poetry", "run", "pytest", "--nbval", "python-examples/auto_test/01_redis-py.ipynb"]