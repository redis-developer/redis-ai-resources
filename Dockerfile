FROM python:3.11

RUN apt-get update && apt-get install -y libgl1-mesa-glx

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
COPY python-examples/auto_test/resources /app/resources


RUN poetry config virtualenvs.create false && poetry install --all-extras

# Run tests
CMD ["tail", "-f", "/dev/null"]
# CMD ["poetry", "run", "pytest", "--nbval", "python-examples/auto_test/01_redis-py.ipynb"]