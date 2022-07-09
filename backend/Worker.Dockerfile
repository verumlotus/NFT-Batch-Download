# 
FROM python:3.9 as requirements-stage

# 
WORKDIR /tmp

# 
RUN pip install poetry

# 
COPY ./backend/pyproject.toml ./backend/poetry.lock* /tmp/

# 
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Create app directory
RUN mkdir /code/app

# 
COPY ./backend /code/app

WORKDIR /code/app

# Need to generate prisma
RUN prisma generate

# 
CMD ["celery", "--app=tasks:app", "worker", "--concurrency=1", "--loglevel=INFO"]
