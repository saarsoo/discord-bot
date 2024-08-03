# Use the official Python image from the Docker Hub
FROM python:3.12

# Set environment variables
ENV POETRY_VERSION=1.4.2

# Install Poetry
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock ./

# Install the dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code into the container
COPY . .

# Specify the command to run the application
CMD ["poetry", "run", "python", "src/discord_bot/app.py"]

# Expose the port the application runs on (optional, if your app serves a web service)
# EXPOSE 5000
