FROM python:3.11-buster
WORKDIR /usr/src/app
COPY requirements.txt ./
# Postgres client dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc
RUN pip install -r requirements.txt
# Para hacer debugging interno a la imagen
# CMD ["tail", "-f", "/dev/null"]
CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "5000", "main:app" ]
