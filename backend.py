from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiofiles
import os
import re

app = FastAPI()

# Static files for CSS/JS/images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Upload folder
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper functions
def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.txt'}

def secure_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = filename.strip().replace(' ', '_')
    filename = re.sub(r'[^\w\-.()]', '', filename)
    return filename

async def save_upload_file(upload_file: UploadFile, destination: str):
    async with aiofiles.open(destination, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)

# Routes
@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("frontend.html", {"request": request, "submitted": False})

@app.post("/submit")
async def submit_form(request: Request, file: UploadFile = File(None), text: str = Form('')):
    error = None
    file_url = None

    if file and not allowed_file(file.filename):
        error = "File type not allowed."
    elif file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, filename)
        await save_upload_file(file, file_path)
        file_url = f"/static/uploads/{filename}"

    # Mock name/email for example; replace with actual fields if required
    response_data = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "file_url": file_url,
        "text": text,
        "error": error
    }

    return JSONResponse(content=response_data)
