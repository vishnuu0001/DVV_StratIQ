FROM python:3.11-slim
WORKDIR /app
RUN pip install hatchling
COPY pyproject.toml .
RUN pip install -e .
COPY src/ src/
COPY schemas/ schemas/
COPY config/ config/
COPY alembic.ini alembic.ini
RUN alembic upgrade head || true
EXPOSE 8003
CMD ["uvicorn", "inspector.main:app", "--host", "0.0.0.0", "--port", "8003"]
