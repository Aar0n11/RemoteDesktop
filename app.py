import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pyautogui
import io
import mss
import json
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from PIL import Image
import os

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as config_file:
        return json.load(config_file)

config = load_config()

app = FastAPI()

frontend_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(frontend_path):
    print(f"Warning: Frontend directory '{frontend_path}' not found!")

app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the main HTML page"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(content={"error": "Frontend not found"}, status_code=404)

@app.get("/config")
def get_config():
    return config  # Serve the config file to the frontend

@app.post("/move-mouse")
async def move_mouse(data: dict):
    try:
        if not all(k in data for k in ("x", "y", "screenWidth", "screenHeight")):
            return JSONResponse(content={"status": "error", "message": "Missing required fields"}, status_code=400)

        x, y, screenWidth, screenHeight = data["x"], data["y"], data["screenWidth"], data["screenHeight"]
        hostScreenWidth, hostScreenHeight = pyautogui.size()

        # Scale the mouse movement to the host screen size
        scaledX = int((x / screenWidth) * hostScreenWidth)
        scaledY = int((y / screenHeight) * hostScreenHeight)

        pyautogui.moveTo(scaledX, scaledY, duration=0.0)
        return {"status": "success", "message": "Mouse moved"}
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error moving mouse: {str(e)}"}, status_code=500)

@app.post("/click")
async def click():
    try:
        pyautogui.click()
        return {"status": "success", "message": "Click successful"}
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error clicking: {str(e)}"}, status_code=500)

@app.post("/mousedown")
async def mousedown():
    pyautogui.mouseDown()
    return {"status": "success", "message": "Mouse down"}

@app.post("/mouseup")
async def mouseup():
    pyautogui.mouseUp()
    return {"status": "success", "message": "Mouse up"}

@app.post("/scroll")
async def scroll(data: dict):
    try:
        pyautogui.scroll(int(data.get("deltaY", 0)))
        return {"status": "success", "message": "Scroll successful"}
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error scrolling: {str(e)}"}, status_code=500)

@app.post("/key")
async def key(data: dict):
    try:
        key_value = data.get("key")
        if not key_value:
            return JSONResponse(content={"status": "error", "message": "Missing key parameter"}, status_code=400)
        
        pyautogui.press(key_value)
        return {"status": "success", "message": f'Key "{key_value}" pressed successfully'}
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error pressing key: {str(e)}"}, status_code=500)

@app.get("/screenshot")
def screenshot():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)

            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            img_io = io.BytesIO()
            img.save(img_io, format="JPEG", quality=config["screenshot_quality"])
            img_io.seek(0)

        return StreamingResponse(img_io, media_type="image/jpeg")
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error capturing screenshot: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config["port"])
