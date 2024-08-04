# Use the official Python image from the Docker Hub
FROM python:3.12

RUN pip install poetry

# Set the working directory in the container
WORKDIR /discord-bot

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock ./

# Install the dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code into the container
COPY src/ src/

RUN poetry install --no-dev --no-interaction --no-ansi
RUN poetry check

RUN useradd -s /bin/bash user

USER user

# Specify the command to run the application
CMD ["python", "src/discord_bot/app.py"]

# Expose the port the application runs on (optional, if your app serves a web service)
# EXPOSE 5000
