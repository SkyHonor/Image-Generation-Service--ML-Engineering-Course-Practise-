FROM python:3.10-slim

WORKDIR /app

# Копируем список библиотек внутрь контейнера
COPY requirements.txt .

# Устанавливаем их внутри Docker
RUN pip install --no-cache-dir -r requirements.txt

CMD ["tail", "-f", "/dev/null"]