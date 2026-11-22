FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "pokedex_backend.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
