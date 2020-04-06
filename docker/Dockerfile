# Dockerfile
# Pull base image
FROM python:3.7
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PROD True
# # Set work directory
WORKDIR /code
# Copy project
COPY . /code/
# Install dependencies
RUN pip install -r /code/requirements.txt
# Collect staticfiles
RUN python manage.py collectstatic --noinput
