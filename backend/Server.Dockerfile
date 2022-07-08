# 
FROM python:3.9 as requirements-stage

# 
WORKDIR /tmp

# 
RUN pip install poetry

# 
COPY ./pyproject.toml ./poetry.lock* /tmp/

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
COPY . /code/app

WORKDIR /code/app

# Need to generate prisma
RUN prisma generate

EXPOSE 80

# 
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
