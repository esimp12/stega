FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /workspace

# Handle third party dependencies
COPY dist/requirements.txt /workspace/requirements.txt
RUN uv pip sync --system requirements.txt

# Install application dependencies
COPY dist/*.whl /workspace/dist/
RUN uv pip install --system dist/*.whl

CMD ["uv", "run", "serve"]