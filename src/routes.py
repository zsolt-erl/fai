from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
import uvicorn
from fastai.vision import *
from io import BytesIO
import aiohttp
import asyncio
import json
import torch

# torch.nn.Module.dump_patches = True

app = Starlette()

defaults.device = torch.device('cpu')
learn = load_learner("/model")


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
    print(">>> got request")
    bytes = await (data["file"].read())
    print(">>> read image file")
    return predict_image_from_bytes(bytes)


@app.route("/classify-url", methods=["GET"])
async def classify_url(request):
    bytes = await get_bytes(request.query_params["url"])
    return predict_image_from_bytes(bytes)


async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    class_, _predictions, losses = learn.predict(img)
    print(json.dumps({
        "prediction": str(class_),
        "scores": sorted(
            zip(learn.data.classes, map(float, losses)),
            key=lambda p: p[1],
            reverse=True
        )
    }))

    return JSONResponse({
        "prediction": str(class_),
        "scores": sorted(
            zip(learn.data.classes, map(float, losses)),
            key=lambda p: p[1],
            reverse=True
        )
    })


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
