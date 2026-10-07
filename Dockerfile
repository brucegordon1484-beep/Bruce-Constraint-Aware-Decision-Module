# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

COPY . /app

ENTRYPOINT ["python", "bruce_simulation.py", "--ci", "--steps", "50"]
