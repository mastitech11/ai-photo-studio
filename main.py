
import io
import gc

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from rembg import remove, new_session


# ---------------------------------
# FastAPI Application
# ---------------------------------

app = FastAPI(title="All In One AI Photo Studio")


# ---------------------------------
# CORS Settings
# ---------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------
# AI Model
# ---------------------------------

_session = None


def get_session():
    global _session

    if _session is None:
        _session = new_session("u2netp")

    return _session


# ---------------------------------
# Image Validation
# ---------------------------------

MAX_FILE_SIZE = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000


async def read_image(file: UploadFile):
    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Please upload an image."
        )

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image must be under 15 MB."
        )

    try:
        image = Image.open(io.BytesIO(data))
        image = ImageOps.exif_transpose(image)

        if image.width * image.height > MAX_IMAGE_PIXELS:
            raise HTTPException(
                status_code=413,
                detail="Image resolution is too large."
            )

        image.load()
        return image

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file."
        )


# ---------------------------------
# Home / Health Check
# ---------------------------------

@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Photo Studio AI",
        "message": "Backend is running."
    }


# ---------------------------------
# AI Background Remover
# ---------------------------------

@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):

    image = await read_image(file)

    try:
        # Reduce image size to save server memory
        image.thumbnail(
            (1600, 1600),
            Image.Resampling.LANCZOS
        )

        image = image.convert("RGBA")

        input_buffer = io.BytesIO()
        image.save(input_buffer, format="PNG")

        input_data = input_buffer.getvalue()

        del image
        del input_buffer

        # Remove background using lightweight AI model
        output_data = remove(
            input_data,
            session=get_session()
        )

        gc.collect()

        return Response(
            content=output_data,
            media_type="image/png"
        )

    except HTTPException:
        raise

    except Exception as e:
        gc.collect()

        raise HTTPException(
            status_code=500,
            detail=f"Background removal failed: {str(e)}"
        )


# ---------------------------------
# Photo Enhancer
# ---------------------------------

@app.post("/enhance")
async def enhance(
    file: UploadFile = File(...),
    scale: int = 2
):

    image = await read_image(file)

    if scale not in (1, 2, 3, 4):
        raise HTTPException(
            status_code=400,
            detail="Scale must be 1, 2, 3, or 4."
        )

    try:
        image = image.convert("RGB")

        width, height = image.size

        if scale > 1:
            image = image.resize(
                (width * scale, height * scale),
                Image.Resampling.LANCZOS
            )

        # Improve contrast
        image = ImageEnhance.Contrast(image).enhance(1.08)

        # Improve color
        image = ImageEnhance.Color(image).enhance(1.06)

        # Improve sharpness
        image = ImageEnhance.Sharpness(image).enhance(1.35)

        image = image.filter(
            ImageFilter.UnsharpMask(
                radius=1.2,
                percent=110,
                threshold=3
            )
        )

        output = io.BytesIO()

        image.save(
            output,
            format="JPEG",
            quality=94,
            optimize=True
        )

        result = output.getvalue()

        image.close()
        output.close()

        gc.collect()

        return Response(
            content=result,
            media_type="image/jpeg"
        )

    except HTTPException:
        raise

    except Exception as e:
        gc.collect()

        raise HTTPException(
            status_code=500,
            detail=f"Photo enhancement failed: {str(e)}"
        )
