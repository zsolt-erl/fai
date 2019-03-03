FROM python:3.7.2 

RUN pip install uvicorn starlette
RUN pip install fastai==1.0.44
RUN pip install aiohttp python-multipart
RUN pip3 install https://download.pytorch.org/whl/cpu/torch-1.0.1.post2-cp37-cp37m-linux_x86_64.whl
RUN pip install torchvision


COPY src /app
COPY model /model
WORKDIR /app

# CMD ["sh"]
CMD ["python", "/app/routes.py"]

