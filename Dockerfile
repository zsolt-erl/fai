FROM python:3.7-stretch as base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    vim \
    ca-certificates \
    python-qt4 \
    libjpeg-dev \
    zip \
    unzip \
    libpng-dev &&\
    rm -rf /var/lib/apt/lists/*


COPY requirements-fastai.txt requirements-fastai.txt
COPY requirements-app.txt requirements-app.txt

RUN pip install -r requirements-fastai.txt
RUN pip install -r requirements-app.txt

FROM python:3.7-slim-stretch

COPY --from=base /usr/local /usr/local
COPY src /app
COPY model /var/fai/model
COPY docker-config.yaml /app/config.yaml
COPY logger_conf.yaml /app/logger_conf.yaml

WORKDIR /app

# CMD ["sh"]
CMD ["python", "routes.py"]
