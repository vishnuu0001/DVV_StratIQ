FROM python:3.11-slim
WORKDIR /app
RUN pip install hatchling
COPY pyproject.toml .
RUN pip install -e .
COPY src/ src/
COPY prompts/ prompts/
COPY alembic.ini alembic.ini
RUN alembic upgrade head || true
EXPOSE 8002
CMD ["uvicorn", "agents.main:app", "--host", "0.0.0.0", "--port", "8002"]
