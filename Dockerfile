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


RUN pip install uvicorn starlette
RUN pip install aiohttp python-multipart

RUN pip install numpy
RUN pip install https://download.pytorch.org/whl/cpu/torch-1.0.1.post2-cp37-cp37m-linux_x86_64.whl
RUN pip install fastai==1.0.44
RUN pip install torchvision


FROM python:3.7-slim-stretch

COPY --from=base /usr/local /usr/local
COPY src /app
# COPY model /model
WORKDIR /app
# CMD ["sh"]
CMD ["python", "/app/routes.py"]
