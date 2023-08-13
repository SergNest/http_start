# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.10
FROM python:3.10

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

COPY pyproject.toml $APP_HOME/pyproject.toml


# Встановимо залежності всередині контейнера
RUN pip install poetry
RUN poetry config virtualenvs.create false

# Скопіюємо інші файли в робочу директорію контейнера
COPY . .

# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 3000

# Expose port 5000 for UDP server
EXPOSE 5000/udp

# Запустимо наш застосунок всередині контейнера
CMD ["python", "main.py"]