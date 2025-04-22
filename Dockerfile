FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y unzip curl && rm -rf /var/lib/apt/lists/* # Add curl and fix cleanup path
RUN pip install --upgrade pip
RUN pip install uv
RUN python -m uv pip install --no-cache-dir -r requirements.txt
RUN python -m uv pip install --upgrade reflex
COPY . .
EXPOSE 3000
EXPOSE 8000
CMD ["reflex", "run"]
