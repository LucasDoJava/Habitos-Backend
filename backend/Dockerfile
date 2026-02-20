FROM python:3.12

WORKDIR /app

COPY backend/requirements.txt .

RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x backend/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["backend/entrypoint.sh"]
