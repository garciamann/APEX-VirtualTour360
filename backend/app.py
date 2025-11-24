from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess, uuid, os, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads/"
OUTPUT_DIR = "converted/"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def detect_projection(input_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", input_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        meta = json.loads(result.stdout)
        tags = meta.get("format", {}).get("tags", {})
        projection = tags.get("projection", "").lower()
        codec = meta["streams"][0].get("codec_name", "")
        if "equirectangular" in projection:
            return "equirectangular"
        elif "cubemap" in projection:
            return "cubemap"
        elif "fisheye" in projection or codec in ["h264", "hevc"]:
            return "dual_fisheye"
        else:
            return "unknown"
    except Exception as e:
        print("Detection failed:", e)
        return "unknown"

@app.post("/upload")
async def upload_insta360(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    ext = os.path.splitext(file.filename)[1].lower()
    output_ext = ".mp4" if ext in [".insv", ".mp4"] else ".jpg"
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}{output_ext}")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    projection_type = detect_projection(input_path)
    print(f"Detected projection: {projection_type}")

    if projection_type == "dual_fisheye":
        filter_str = "v360=input=dual_fisheye:output=equirect"
    elif projection_type == "cubemap":
        filter_str = "v360=input=cube3x2:output=equirect"
    else:
        filter_str = "null"

    if ext in [".insv", ".mp4"]:
        subprocess.run(["ffmpeg", "-i", input_path, "-vf", filter_str, "-c:v", "libx264", "-crf", "18", output_path], check=True)
    elif ext in [".jpg", ".jpeg"]:
        subprocess.run(["ffmpeg", "-i", input_path, "-vf", filter_str, output_path], check=True)

    return {"message": "File converted successfully!", "url": f"{output_path}"}
