from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove, new_session
import io
app=FastAPI(title="Photo Studio AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=False,allow_methods=["*"],allow_headers=["*"])
_session=None
def get_session():
    global _session
    if _session is None: _session=new_session("u2netp")
    return _session
@app.get("/")
def health(): return {"status":"ok","service":"Photo Studio AI"}
@app.post("/remove-background")
async def remove_background(file:UploadFile=File(...)):
    data=await file.read()
    if len(data)>15*1024*1024: raise HTTPException(413,"Image must be under 15 MB")
    try: return Response(content=remove(data,session=get_session()),media_type="image/png")
    except Exception as e: raise HTTPException(500,str(e))
@app.post("/enhance")
async def enhance(file:UploadFile=File(...),scale:int=2):
    data=await file.read()
    if len(data)>15*1024*1024: raise HTTPException(413,"Image must be under 15 MB")
    if scale not in (1,2,3,4): raise HTTPException(400,"Scale must be 1, 2, 3, or 4")
    try:
        im=Image.open(io.BytesIO(data)).convert("RGB"); w,h=im.size
        if scale>1: im=im.resize((w*scale,h*scale),Image.Resampling.LANCZOS)
        im=ImageEnhance.Contrast(im).enhance(1.08)
        im=ImageEnhance.Color(im).enhance(1.06)
        im=ImageEnhance.Sharpness(im).enhance(1.35)
        im=im.filter(ImageFilter.UnsharpMask(radius=1.2,percent=110,threshold=3))
        out=io.BytesIO(); im.save(out,format="JPEG",quality=94,optimize=True)
        return Response(content=out.getvalue(),media_type="image/jpeg")
    except Exception as e: raise HTTPException(500,str(e))
