ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "agent.py"]
