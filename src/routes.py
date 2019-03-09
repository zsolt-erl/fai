from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
import uvicorn
from fastai.vision import *
from io import BytesIO
import aiohttp
import asyncio
import json
import torch
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, PatternMatchingEventHandler
import logging.config
import yaml
from dynaconf import settings

print(settings)


app = Starlette()


@app.route("/")
def form(request):
    return HTMLResponse("""
        <h3>This app will classify images using a model generated with fastai<h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            Select image to upload:
            <input type="file" name="file">
            <input type="submit" value="Upload Image">
        </form>
        Or submit a URL:
        <form action="/classify-url" method="get">
            <input type="url" name="url">
            <input type="submit" value="Fetch and analyze image">
        </form>
    """)


@app.route("/upload", methods=["POST"])
async def upload(request):
    data = await request.form()
    logging.debug("got upload request")

    bytes = await (data["file"].read())
    print("read image file: %s", data["file"])

    return predict_image_from_bytes(bytes)


@app.route("/classify-url", methods=["GET"])
async def classify_url(request):
    logging.debug("got classify-url request")
    bytes = await get_bytes(request.query_params["url"])
    return predict_image_from_bytes(bytes)


async def get_bytes(url):
    logging.debug("getting image from %s", url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


def predict_res(class_, label, probabilities):
    return {
        "prediction": str(class_),
        "scores": sorted(
            zip(learn.data.classes, map(float, probabilities)),
            key=lambda p: p[1],
            reverse=True
        )
    }


def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    lp = learn.predict(img)
    return JSONResponse(predict_res(*lp))


class NewImageFileHandler(PatternMatchingEventHandler):
    def on_created(self, event):
        logging.info("found new image: %s", event.src_path)
        img = open_image(event.src_path)
        lp = learn.predict(img)
        predLog = {"image_file": event.src_path, "result": predict_res(*lp)}
        predLogger.info(predLog)


def watch_for_images(path):
    observer = Observer()
    event_handler = NewImageFileHandler(patterns=["*.jpg", "*.png"])
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    return observer


if __name__ == '__main__':
    # read main config file
    with open('./config.yaml', 'r') as stream:
        config = yaml.load(stream)

    # set up loggers
    with open('./logger_conf.yaml', 'r') as stream:
        log_config = yaml.load(stream)
    if "predictionLog" in config:
        log_config["handlers"]["file"]["filename"] = config["predictionLog"]

    logging.config.dictConfig(log_config)
    predLogger = logging.getLogger('predLogger')

    # torch.nn.Module.dump_patches = True

    defaults.device = torch.device('cpu')
    learn = load_learner(config["modelDir"])
    obs = watch_for_images(config["imageDir"])
    uvicorn.run(app, host='0.0.0.0', port=8000)
    obs.stop()
