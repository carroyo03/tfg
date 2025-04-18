FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install uv
RUN python -m uv pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["reflex", "run"]
